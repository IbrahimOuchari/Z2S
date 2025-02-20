from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "stock.quant"

    ref_product_client = fields.Char('product.template', related="product_id.ref_product_client")
    description_sale = fields.Text('product.template', related="product_id.description_sale")


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_stock = fields.Float('product.template', related="product_id.qty_available")

