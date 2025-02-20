from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order.line"

    top_order_id = fields.Many2one('name')


### create new class for Top Selling Products with amount
class TopsellingProducts(models.Model):
    _name = "sale.products"
    _order = 'amount desc'
    _description = 'Sale Products'

    product = fields.Many2one('product.product', string='Produit')
    amount = fields.Float(string='Valeur')


### create a new class for Top Selling Products with Quantity
class TopsellingProducts(models.Model):
    _name = "sale.quantity"
    _order = 'quantity desc'
    _description = 'Sale Quantity'

    product = fields.Many2one('product.product', string='Produit')
    quantity = fields.Float(string='Quantité')
