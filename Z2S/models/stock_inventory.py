from odoo import fields, models, api, _


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _description = "Inventory Line"

    client_id = fields.Many2one('res.partner', string="Client", related="product_id.client_id")
