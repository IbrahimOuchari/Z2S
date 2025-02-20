from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    field_to_trigger = fields.Boolean('Trigger Productivity Calculation')

    @api.onchange('field_to_trigger')
    def _onchange_field_to_trigger(self):
        if self.field_to_trigger:
            for order in self:
                # Call the _compute_productivity method if the field is set to True
                order._compute_productivity()