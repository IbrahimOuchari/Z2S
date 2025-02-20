from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.tools import config


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Ajouter boutton d'archivage '

    active = fields.Boolean(default=True)

    # modification de sale order en adéquation avec devis

    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('validation', 'Attente Validation'),
        ('accepte', 'BC Accepté'),
        ('sale', 'Sales Order'),
        ('fait', 'Fait'),
        ('rejete', 'Rejeté'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='brouillon')
    devis_seq = fields.Char(string='Référence Devis', readonly=True)

    def action_draft_bc(self):
        orders = self.filtered(lambda s: s.state in ['cancel', 'sent', 'rejete', 'sale'])
        return orders.write({
            'state': 'brouillon',
            'signature': False,
            'signed_by': False,
            'signed_on': False,
        })

    date_order = fields.Date(string='Order Date', required=True, readonly=True, index=True,
                             states={'brouillon': [('readonly', False)], 'sale': [('readonly', False)],
                                     'sent': [('readonly', False)]}, copy=False,
                             default=fields.Datetime.now)
    partner_id = fields.Many2one(
        'res.partner', string='Client', readonly=True,
        states={'brouillon': [('readonly', False)]},
        required=True, change_default=True, tracking=True,
        domain="['|', ('customer_rank','>', 0),('is_customer','=',True)]", )

    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        required=True, readonly=True, states={'brouillon': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'fait': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    # -------------------------------------------------------------------------------------

    # Masquer le bouton modifier selon state
    hide_edit = fields.Html(string='Hide Edit', sanitize=False, compute='_compute_hide', store=False)

    @api.depends('state')
    def _compute_hide(self):
        for record in self:
            if record.state != 'brouillon' and not self.env.user.has_group('bmg_sale.valide_bc_vente'):
                record.hide_edit = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit = False

        # Imprimer BC

    def print_report(self):
        # Assurez-vous qu'il y a un seul enregistrement pour générer le rapport
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('sale.action_report_saleorder')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

    # Action confirmaion BC

    motif_validation_bc = fields.Text(string="Raison de Refus BC")
    bc_annule = fields.Boolean('BC Annulé')

    def action_save_bc(self):
        for rec in self:
            rec.state = 'validation'

    def action_validation_bc(self):
        for rec in self:
            rec.state = 'accepte'

    def action_rejet_bc(self):
        for rec in self:
            rec.bc_annule = True

        action = self.env.ref('bmg_sale.action_wizard_cancel_reason_bc').read()[0]
        action['context'] = {
            'default_bc_id': self.id,
        }
        return action

    def action_in_draft(self):
        for rec in self:
            rec.state = 'brouillon'
