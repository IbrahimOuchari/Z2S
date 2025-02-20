from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class PurchaseRfq(models.Model):
    _name = "purchase.rfq"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "New Page Demande de Prix Modules"

    name = fields.Char(string='Sequence Rfq', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('Nouveau'))

    # Sequence de demande d'achat
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.rfq') or _('Nouveau')
        return super(PurchaseRfq, self).create(vals)

    priority = fields.Selection(
        [('0', 'Normal'), ('1', 'Urgent')], 'Priority', default='0', index=True)
    date_rfq = fields.Date('Date', required=True, index=True, copy=False,
                           default=fields.Datetime.now)

    partner_id = fields.Many2one('res.partner', string='Fournisseur', required=True, change_default=True, tracking=True,
                                 domain="[ ('is_supplier', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    partner_ref = fields.Char('Référence Fournisseur', copy=False,
                              help="Référence de la commande du fournisseur")

    state = fields.Selection([
        ('rfq', 'Demande d\'Achat'),
        ('sent', 'Envoyé'),
        ('validation', 'Attente Validation'),
        ('confirme', 'Validée'),
        ('nonvalide', 'Rejetée'),
        ('expired', 'Expiré'),
        ('commande', 'Commandée'),
        ('cancel', 'Annulé'),
    ], string='Status', readonly=True, index=True, copy=False, default='rfq', tracking=True)

    # Imprimer devis
    def print_report(self):
        # Assurez-vous qu'il y a un seul enregistrement pour générer le rapport
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('bmg_achat.action_da_template')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

    # Masquer le bouton modifier selon state
    hide_edit = fields.Html(string='Hide Edit', sanitize=False, compute='_compute_hide', store=False)

    @api.depends('state')
    def _compute_hide(self):
        for record in self:
            if record.state != 'rfq' and not self.env.user.has_group('bmg_achat.valide_da'):
                record.hide_edit = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit = False

        # Action confirmaion DA

    motif_validation_da = fields.Text(string="Raison de Refus D.A.")
    da_annule = fields.Boolean('DA Annulé')

    def action_save_da(self):
        for rec in self:
            rec.state = 'validation'

    def action_validation_da(self):
        for rec in self:
            rec.state = 'confirme'

    def action_invalidation_da(self):
        for rec in self:
            rec.da_annule = True

        action = self.env.ref('bmg_achat.action_wizard_cancel_reason_da').read()[0]
        action['context'] = {
            'default_da_id': self.id,
        }
        return action

    def action_in_draft_da(self):
        for rec in self:
            rec.state = 'rfq'

    READONLY_STATES = {
        'confirme': [('readonly', True)],
        'expired': [('readonly', True)],
        'cancel': [('readonly', True)],
    }
    notes = fields.Text('Conditions')

    currency_id = fields.Many2one('res.currency', 'Devise', required=True, states=READONLY_STATES,
                                  default=lambda self: self.env.company.currency_id.id)
    rfq_line = fields.One2many('purchase.rfq.line', 'rfq_id', string='Rfq Lines',
                               states={'cancel': [('readonly', True)], 'confirme': [('readonly', True)]}, copy=True)
    date_planned = fields.Date(string='Date Prévue de Réception', index=True, copy=False,
                               compute='_compute_date_planned',
                               store=True, readonly=False)

    payment_term_id = fields.Many2one('account.payment.term', 'Condition de Paiement',
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_id = fields.Many2one('product.product', related='rfq_line.product_id', string='Produit', readonly=False)
    user_id = fields.Many2one(
        'res.users', string='Responsable Achat', index=True, tracking=True,
        default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', 'Société', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position',
                                         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    @api.depends('rfq_line.date_planned')
    def _compute_date_planned(self):
        """ date_planned = the earliest date_planned across all order lines. """
        for order in self:
            dates_list = order.rfq_line.filtered(lambda x: not x.display_type and x.date_planned).mapped(
                'date_planned')
            if dates_list:
                order.date_planned = fields.Datetime.to_string(min(dates_list))
            else:
                order.date_planned = False

    @api.onchange('date_planned')
    def onchange_date_planned(self):
        if self.date_planned:
            self.rfq_line.filtered(lambda line: not line.display_type).date_planned = self.date_planned

    def write(self, vals):
        vals, partner_vals = self._write_partner_values(vals)
        res = super().write(vals)
        if partner_vals:
            self.partner_id.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res

    def copy(self, default=None):
        ctx = dict(self.env.context)
        ctx.pop('default_product_id', None)
        self = self.with_context(ctx)
        new_po = super(PurchaseRfq, self).copy(default=default)
        return new_po

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        # Ensures all properties and fiscal positions
        # are taken with the company of the order
        # if not defined, with_company doesn't change anything.
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.fiscal_position_id = False
            self.currency_id = self.env.company.currency_id.id
        else:
            self.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id)
            self.payment_term_id = self.partner_id.property_supplier_payment_term_id.id
            self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id
        return {}

    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        if not self.partner_id or not self.env.user.has_group('purchase.group_warning_purchase'):
            return
        warning = {}
        title = False
        message = False

        partner = self.partner_id

        # If partner has no warning, check its company
        if partner.purchase_warn == 'no-message' and partner.parent_id:
            partner = partner.parent_id

        if partner.purchase_warn and partner.purchase_warn != 'no-message':
            # Block if partner only has warning but parent company is blocked
            if partner.purchase_warn != 'block' and partner.parent_id and partner.parent_id.purchase_warn == 'block':
                partner = partner.parent_id
            title = _("Warning for %s", partner.name)
            message = partner.purchase_warn_msg
            warning = {
                'title': title,
                'message': message
            }
            if partner.purchase_warn == 'block':
                self.update({'partner_id': False})
            return {'warning': warning}
        return {}

    def _write_partner_values(self, vals):
        partner_values = {}
        if 'receipt_reminder_email' in vals:
            partner_values['receipt_reminder_email'] = vals.pop('receipt_reminder_email')
        if 'reminder_date_before_receipt' in vals:
            partner_values['reminder_date_before_receipt'] = vals.pop('reminder_date_before_receipt')
        return vals, partner_values

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def create_order(self):
        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner_id.id,
            'order_type': self.order_type.id,
            'user_id': self.user_id.id,
            'payment_term_id': self.payment_term_id.id,
            'date_planned': self.date_planned,
            'currency_id': self.currency_id.id,
            'rfq_seq': self.name,
            'order_line': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
                'taxes_id': line.tax_id,

            }) for line in self.rfq_line],
        })
        self.state = "commande"
        return {
            'name': 'Purchase Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current', }
        return

    # Calcul montant total

    amount_untaxed = fields.Monetary(string='Montant H.T.', store=True, readonly=True, compute='_amount_all',
                                     digits='Product Price',
                                     tracking=5)
    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group',
                                    help="type: [(name, amount, base, formated amount, formated base)]")
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 digits='Product Price')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   digits='Product Price', tracking=4)

    @api.depends('rfq_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.rfq_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.rfq_line:
                price_reduce = line.price_unit
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_qty, product=line.product_id,
                                                partner=order.partner_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]


class PurchaseRfqLine(models.Model):
    _name = "purchase.rfq.line"
    _description = "Purchase RFQ Line"
    _rfq = 'rfq_id, sequence, id'

    name = fields.Text(string='Désignation', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True)
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    date_planned = fields.Date(string='Date de Réception', index=True)
    product_uom = fields.Many2one('uom.uom', string='UdM',
                                  domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Article', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    product_type = fields.Selection(related='product_id.type', readonly=True)

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ Reference', index=True, required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company.id)

    state = fields.Selection(related='rfq_id.state', store=True, readonly=False)

    partner_id = fields.Many2one('res.partner', related='rfq_id.partner_id', string='Fournisseur', readonly=True,
                                 store=True)
    currency_id = fields.Many2one('res.currency', 'Devise', related='rfq_id.currency_id', )
    date_rfq = fields.Date(related='rfq_id.date_rfq', string='Date demande', readonly=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)

    price_unit = fields.Float(string='P.U.', digits='Product Price')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    price_tax = fields.Float(compute='_compute_amount_tax', string='Total Tax', readonly=True, store=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.description_purchase
            self.product_uom = self.product_id.uom_po_id.id
            self.tax_id = self.product_id.supplier_taxes_id.ids

    price_subtotal = fields.Monetary(compute='_compute_amount_ht', string='Montant H.T.', digits='Product Price',
                                     readonly=True, store=True)

    @api.depends('product_qty', 'price_unit')
    def _compute_amount_ht(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.product_qty

    @api.depends('price_subtotal', 'tax_id')
    def _compute_amount_tax(self):
        for line in self:
            line.price_tax = line.price_subtotal * (line.tax_id.amount / 100)

