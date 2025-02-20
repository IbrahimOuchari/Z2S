from odoo import api, fields, models


class AMLPU(models.Model):
    _inherit = 'account.move.line'

    pu_avec_remise = fields.Float(string='P.U. Après Remise', digits='Product Price', readonly=True,
                                  compute='_pu_avec_remise', )

    @api.depends('discount', 'price_unit')
    def _pu_avec_remise(self):
        for compute in self:
            compute.pu_avec_remise = ((100 - compute.discount) / 100) * compute.price_unit
