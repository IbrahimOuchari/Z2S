from odoo import _, api, fields, models
from odoo.exceptions import UserError

class select_of_picking(models.TransientModel):
    _name = "select.of.picking"
    _description = "Select OF from picking"

    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)

    of_id = fields.Many2one('mrp.production',
                             string="Ordre de Fabrication",

                             )




