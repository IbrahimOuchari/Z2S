from odoo import fields, models, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Archivage de BC Achat
    active = fields.Boolean(default=True)

    @api.model
    def _get_default_description_achat(self):
        # Récupérer l'instance de res.config.settings
        config_settings = self.env['res.config.settings'].sudo().get_values()
        # Récupérer la valeur de description_achat depuis l'instance
        return config_settings.get('description_achat', False)

    description_achat = fields.Text(string="Conditions Générales", default=_get_default_description_achat)
    note = fields.Text('Terms and conditions')

    rfq_seq = fields.Char(string='Référence RFQ', readonly=True)

    def button_draft_achat(self):
        self.write({'state': 'brouillon'})
        return {}

    def button_confirm_bc_achat(self):
        for rec in self:
            rec.state = 'purchase'

    # Imprimer BC
    def print_report(self):
        # Assurez-vous qu'il y a un seul enregistrement pour générer le rapport
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('purchase.action_report_purchase_order')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

        # Action confirmaion BC Achat

    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('draft', 'RFQ'),
        ('validation', 'Attente Validation'),
        ('confirme', 'BC Accepté'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('rejete', 'Rejeté'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='brouillon', tracking=True)

    motif_validation_bc = fields.Text(string="Raison de Refus BC Achat")
    bc_achat_annule = fields.Boolean('BC Annulé')

    def action_save_bc(self):
        for rec in self:
            rec.state = 'validation'

    def action_validation_bc(self):
        for rec in self:
            rec.state = 'confirme'

    def action_invalidation_bc(self):
        for rec in self:
            rec.bc_achat_annule = True
        action = self.env.ref('bmg_achat.action_wizard_cancel_reason_bc_achat').read()[0]
        action['context'] = {
            'default_bc_id': self.id,
        }
        return action

    def action_in_draft_bc(self):
        for rec in self:
            rec.state = 'brouillon'


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    description_achat = fields.Text(string="Conditions Générales")

    @api.model
    def get_values(self):
        res = super().get_values()
        description_achat = self.env['ir.config_parameter'].sudo().get_param('bmg_achat.description_achat')
        res.update(
            description_achat=description_achat,
        )
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('bmg_achat.description_achat', self.description_achat)
