from odoo import models, fields, api


class GcsSale(models.Model):
    _inherit = 'purchase.rfq'

    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id)
    type_of_signature = fields.Char(string='Type of Signature', compute='_compute_default_values')
    is_purchase_rfq = fields.Boolean(string='Is Purchase RFQ', compute='_compute_default_values')
    signature_position = fields.Boolean(string='Signature Position At Left', compute='_compute_default_values')
    sign = fields.Boolean(string="Ajouter une Signature", default=True)

    @api.onchange('id')
    def _compute_default_values(self):
        settings = self.env["res.config.settings"]
        signature_option = settings.get_setting()['signature_option']
        is_purchase_rfq = settings.get_purchase_rfq()
        signature_position = settings.get_signature_position()
        for rec in self:
            rec.type_of_signature = signature_option
            rec.is_purchase_rfq = is_purchase_rfq
            rec.signature_position = signature_position
