from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    # Boolean field to check if the user belongs to the group
    user_has_group_access = fields.Boolean(string="User Has Access to Be Consumed", compute="_compute_user_has_group_access")

    @api.depends('user_has_group_access')
    def _compute_user_has_group_access(self):
        for record in self:
            # Check if the user has the 'of_access_to_tobe_consumed' group
            record.user_has_group_access = self.env.user.has_group('nn_Z2S.of_access_to_tobe_consumed')
