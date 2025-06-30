from odoo import models, api, _, fields
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.bom_id = False  # Always clear bom_id when product_tmpl_id changes
