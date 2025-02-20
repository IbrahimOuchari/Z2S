from odoo import models, fields

class ReturnLines(models.Model):
    _name = 'return.lines'
    _description = 'Return Lines'

    production_id = fields.Many2one('mrp.production', string="Production Order", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float(string="Quantity to Return", required=True)
    quantity_left = fields.Float(string="Quantity Left", required=True)
    move_id = fields.Many2one('stock.move', string="Stock Move")
