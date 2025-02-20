from odoo import fields, models, api, _
from functools import partial
from odoo.tools.misc import formatLang, get_lang
from datetime import datetime, timedelta


class SaleDevis(models.Model):
    _name = "sale.devis"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "New Page Sales Devis Modules"

    name = fields.Char(string='Sequence Devis', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('Nouveau'))
    partner_id = fields.Many2one(
        'res.partner', string='Client',
        state={'devis': [('readonly', False)]},
        required=True, change_default=True, tracking=True, index=True,
        domain="['|', ('customer_rank','>', 0),('is_customer','=',True)]", )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validation', 'Attente Validation'),
        ('devis', 'Devis Validé'),
        ('confirme', 'Commande'),
        ('nonvalide', 'Non Validé'),
        ('cancel', 'Non Concrétisé'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft', store=True)

    motif_validation_devis = fields.Text(string="Raison de Refus Devis")

    # Masquer le bouton modifier selon state
    hide_edit = fields.Html(string='Hide Edit', sanitize=False, compute='_compute_hide', store=False)

    @api.depends('state')
    def _compute_hide(self):
        for record in self:
            if record.state != 'draft' and not self.env.user.has_group('bmg_sale.valide_devis'):
                record.hide_edit = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit = False

    # Imprimer devis
    def print_report(self):
        # Assurez-vous qu'il y a un seul enregistrement pour générer le rapport
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('bmg_sale.action_devis_template')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

    # Action confirmaion Devis

    devis_annule = fields.Boolean('Devis Annulé')

    def action_save_devis(self):
        for rec in self:
            rec.state = 'validation'

    def action_validation_devis(self):
        for rec in self:
            rec.state = 'devis'

    def action_invalidation_devis(self):
        for rec in self:
            rec.devis_annule = True

        action = self.env.ref('bmg_sale.action_wizard_cancel_reason_devis').read()[0]
        action['context'] = {
            'default_devis_id': self.id,
        }
        return action

    def action_in_draft(self):
        for rec in self:
            rec.state = 'draft'

    # Action dupliquer
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'devis_line' not in default:
            default['devis_line'] = [(0, 0, line.copy_data()[0]) for line in
                                     self.devis_line]
        return super(SaleDevis, self).copy_data(default)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    # Sequence de devis
    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('Nouveau'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.devis') or _('Nouveau')
        return super(SaleDevis, self).create(vals)

    def _default_validity_date(self):
        if self.env['ir.config_parameter'].sudo().get_param('sale.use_quotation_validity_days'):
            days = self.env.company.quotation_validity_days
            if days > 0:
                return fields.Date.to_string(datetime.now() + timedelta(days))
        return False

    @api.depends('validity_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for order in self:
            order.is_expired = order.state == 'devis' and order.validity_date and order.validity_date < today

    @api.depends('is_expired', 'state')
    def _compute_expired_state(self):
        for state in self:
            if state.is_expired:
                state.status_devis = '3'
            elif state.state == 'validation':
                state.status_devis = 'validation'
            elif state.state == 'devis':
                state.status_devis = 'devis'
            elif state.state == 'confirme':
                state.status_devis = 'confirme'
            elif state.state == 'nonvalide':
                state.status_devis = 'nonvalide'
            elif state.state == 'cancel':
                state.status_devis = 'cancel'
            else:
                state.status_devis = 'draft'

    status_devis = fields.Selection([
        ('draft', 'Brouillon'),
        ('validation', 'Attente Validation'),
        ('devis', 'Devis Validé'),
        ('confirme', 'Commande'),
        ('nonvalide', 'Non Validé'),
        ('cancel', 'Non Concrétisé'),
        ('3', 'Expiré'),
    ],
        string="Status Devis",
        default="draft", readonly=True, compute="_compute_expired_state", store=True)

    is_expired = fields.Boolean(compute='_compute_is_expired', string="Expiré")

    date_devis = fields.Date(string='Date Devis', required=True)
    validity_date = fields.Date(string='Date d\'Expiration', required=True, default=_default_validity_date)
    company_id = fields.Many2one('res.company', 'Société', required=True, index=True,
                                 default=lambda self: self.env.company)

    payment_term_id = fields.Many2one('account.payment.term', string='Condition de paiement', check_company=True,
                                      domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", )

    sale_order_template_id = fields.Many2one(
        'sale.order.template', 'Modèle de Devis',
        readonly=True, check_company=True,
        states={'devis': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    # get le modèle de devis
    @api.model
    def default_get(self, fields_list):
        default_vals = super(SaleDevis, self).default_get(fields_list)
        if "sale_order_template_id" in fields_list and not default_vals.get("sale_order_template_id"):
            company_id = default_vals.get('company_id', False)
            company = self.env["res.company"].browse(company_id) if company_id else self.env.company
            default_vals['sale_order_template_id'] = company.sale_order_template_id.id
        return default_vals

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if self.sale_order_template_id and self.sale_order_template_id.number_of_days > 0:
            default = dict(default or {})
            default['validity_date'] = fields.Date.context_today(self) + timedelta(
                self.sale_order_template_id.number_of_days)
        return super(SaleDevis, self).copy(default=default)

    def _compute_line_data_for_template_change(self, line):
        return {
            'display_type': line.display_type,
            'name': line.name,

        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleDevis, self).onchange_partner_id()
        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)
        self.note = template.note or self.note

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):

        template = self.sale_order_template_id.with_context(lang=self.partner_id.lang)

        # --- first, process the list of products from the template
        devis_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)

            if line.product_id:
                price = line.product_id.lst_price
                discount = 0

                if self.pricelist_id:
                    pricelist_price = self.pricelist_id.with_context(uom=line.product_uom_id.id).get_product_price(
                        line.product_id, 1, False)

                    if self.pricelist_id.discount_policy == 'without_discount' and price:
                        discount = max(0, (price - pricelist_price) * 100 / price)
                    else:
                        price = pricelist_price

                data.update({
                    'price_unit': price,
                    'discount': discount,
                    'qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                })

            devis_lines.append((0, 0, data))

        self.devis_line = devis_lines

        # then, process the list of optional products from the template
        option_lines = [(5, 0, 0)]
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))

        self.devis_line_option = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.context_today(self) + timedelta(template.number_of_days)

        if template.note:
            self.note = template.note

    devis_line = fields.One2many('sale.devis.line', 'devis_id', string='Ligne de Devis')

    def _get_update_prices_lines(self):
        return self.order_line.filtered(lambda line: not line.display_type)

    def update_prices(self):
        self.ensure_one()
        for line in self._get_update_prices_lines():
            line.product_uom_change()
            line.discount = 0  # Force 0 as discount for the cases when _onchange_discount directly returns
            line._onchange_discount()
        self.show_update_pricelist = False
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ",
                                 self.pricelist_id.display_name))

    show_update_pricelist = fields.Boolean(string='Has Pricelist Changed')

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Liste des Prix', check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1)
    currency_id = fields.Many2one('res.currency', compute='_compute_currency', store=True, digits=(12, 6),
                                  readonly=True, compute_sudo=True)
    tag_ids = fields.Many2many('crm.tag', 'tag_id', string='Tags')
    user_id = fields.Many2one(
        'res.users', string='Commercial', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ), )
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True, default=_get_default_team, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Position Fiscale',
        domain="[('company_id', '=', company_id)]", check_company=True)

    @api.depends('pricelist_id')
    def _compute_currency(self):
        for record in self:
            if record.pricelist_id:
                record.currency_id = record.pricelist_id.currency_id
            else:
                record.currency_id = record.company_id.currency_id

    @api.onchange('pricelist_id', 'devis_line')
    def _onchange_pricelist_id(self):
        if self.devis_line and self.pricelist_id and self._origin.pricelist_id != self.pricelist_id:
            self.show_update_pricelist = True
        else:
            self.show_update_pricelist = False

    note = fields.Text('Terms and conditions')
    devis_terms = fields.Text(related="pricelist_id.devis_terms")

    # Total Devis

    amount_untaxed = fields.Monetary(string='Montant H.T.', store=True, readonly=True, compute='_amount_all',
                                     digits='Product Price',
                                     tracking=5)
    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group',
                                    help="type: [(name, amount, base, formated amount, formated base)]")
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all',
                                 digits='Product Price')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all',
                                   digits='Product Price', tracking=4)

    # currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True,
    #                         digits=(12, 6), readonly=True,)

    @api.depends('devis_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.devis_line:
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
            for line in order.devis_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.qty, product=line.product_id,
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

    devis_line_option = fields.One2many('sale.devis.line.option', 'devis_id', string='Article Optionnel')

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param(
                'account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],
                                   user_id=user_id)
        self.update(values)

    # Création BC depuis le Devis

    def create_order(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'devis_seq': self.name,
            'payment_term_id': self.payment_term_id.id,
            'order_line': [(0, 0, {
                'display_type': line.display_type,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.qty,
                'price_unit': line.price_unit,
                'discount': line.discount,
            }) for line in self.devis_line],
        })
        self.state = "confirme"
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
            'target': 'current', }
        return

    # en mutli company

    @api.constrains('company_id', 'devis_line')
    def _check_order_line_company_id(self):
        for order in self:
            companies = order.devis_line.product_id.company_id
            if companies and companies != order.company_id:
                bad_products = order.devis_line.product_id.filtered(
                    lambda p: p.company_id and p.company_id != order.company_id)
                raise ValidationError(_(
                    "Votre devis contient des produits de la société %(product_company)s alors que votre devis appartient à la société %(quote_company)s. \n Veuillez modifier la société de votre devis ou supprimer les produits d'autres sociétés (%(bad_products)s).",
                    product_company=', '.join(companies.mapped('display_name')),
                    quote_company=order.company_id.display_name,
                    bad_products=', '.join(bad_products.mapped('display_name')),
                ))

    # fin


class SaleDevisLine(models.Model):
    _name = 'sale.devis.line'
    _description = 'Sales Devis Line'

    name = fields.Text(string='Description', index=True, required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    devis_id = fields.Many2one('sale.devis', string='Devis Reference', required=True, ondelete='cascade', index=True,
                               copy=False)

    state = fields.Selection(related="devis_id.state")
    partner_id = fields.Many2one(related="devis_id.partner_id")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unité de Mesure')
    price_unit = fields.Float(string='P.U.', digits='Product Price')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    discount = fields.Float(string='Remise (%)', digits='Discount', default=0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    pu_remise = fields.Float(string='P.U. Après Remise', compute='_compute_amount_pu_remise', digits='Product Price')
    price_subtotal = fields.Monetary(compute='_compute_amount_ht', string='Montant H.T.', digits='Product Price',
                                     readonly=True, store=True)
    currency_id = fields.Many2one(related='devis_id.currency_id', depends=['devis_id.currency_id'], store=True,
                                  string='Devise', readonly=True)
    price_tax = fields.Float(compute='_compute_amount_tax', string='Total Tax', readonly=True, store=True)
    company_id = fields.Many2one(related='devis_id.company_id', string='Société', required=True, index=True, )

    # ligne de devis à partir de modèle

    # @api.onchange('product_id')
    # def product_id_change(self):
    #     domain = super(SaleDevisLine, self).product_id_change()
    #     if self.product_id and self.devis_id.sale_order_template_id:
    #         for line in self.devis_id.sale_order_template_id.sale_order_template_line_ids:
    #             if line.product_id == self.product_id:
    #                 lang = self.devis_id.partner_id.lang
    #                 self.name = line.with_context(lang=lang).name + self.with_context(
    #                     lang=lang)._get_sale_order_line_multiline_description_variants()
    #                 break
    #     return domain

    # Remplir les lignes de devis avec les champs articles
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.description_sale
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids

    # Calcul Total ligne devis
    @api.depends('discount', 'price_unit')
    def _compute_amount_pu_remise(self):
        for line in self:
            if line.discount:
                line.pu_remise = line.price_unit * ((100 - line.discount) / 100)
            else:
                line.pu_remise = 0

    @api.depends('qty', 'price_unit', 'pu_remise')
    def _compute_amount_ht(self):
        for line in self:
            if line.discount == 0:
                line.price_subtotal = line.price_unit * line.qty
            else:
                line.price_subtotal = line.pu_remise * line.qty

    @api.depends('price_subtotal', 'tax_id')
    def _compute_amount_tax(self):
        for line in self:
            line.price_tax = line.price_subtotal * (line.tax_id.amount / 100)


class SaleDevisLineOption(models.Model):
    _name = 'sale.devis.line.option'
    _description = 'Sales Devis Line Option'

    name = fields.Text(string='Description', index=True, required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    devis_id = fields.Many2one('sale.devis', string='Devis Reference', required=True, ondelete='cascade', index=True,
                               copy=False)
    partner_id = fields.Many2one(related="devis_id.partner_id")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantité', digits='Product Unit of Measure', required=True, )
    product_uom = fields.Many2one('uom.uom', string='Unité de Mesure')
    price_unit = fields.Float(string='P.U.', digits='Product Price')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    discount = fields.Float(string='Remise (%)', digits='Discount', default=0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    pu_remise = fields.Float(string='P.U. Après Remise', compute='_compute_amount_pu_remise', digits='Product Price')
    price_subtotal = fields.Monetary(compute='_compute_amount_ht', string='Montant H.T.', readonly=True,
                                     digits='Product Price', store=True)
    currency_id = fields.Many2one(related='devis_id.currency_id', depends=['devis_id.currency_id'], store=True,
                                  string='Devise', readonly=True)
    price_tax = fields.Float(compute='_compute_amount_tax', string='Total Tax', readonly=True, store=True)

    # Remplir les lignes de devis avec les champs articles
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids

    # Calcul Total ligne devis
    @api.depends('discount', 'price_unit')
    def _compute_amount_pu_remise(self):
        for line in self:
            if line.discount:
                line.pu_remise = line.price_unit * ((100 - line.discount) / 100)
            else:
                line.pu_remise = 0

    @api.depends('qty', 'price_unit', 'pu_remise')
    def _compute_amount_ht(self):
        for line in self:
            if line.discount == 0:
                line.price_subtotal = line.price_unit * line.qty
            else:
                line.price_subtotal = line.pu_remise * line.qty

    @api.depends('price_subtotal', 'tax_id')
    def _compute_amount_tax(self):
        self.price_tax = self.price_subtotal * (self.tax_id.amount / 100)


class PriceListe(models.Model):
    _inherit = 'product.pricelist'

    devis_terms = fields.Text(string='Conditions de Devis par Défaut')
    use_devis_terms = fields.Boolean(
        string='Termes et Conditions Devis par Défaut')
