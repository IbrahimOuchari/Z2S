from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale = fields.Text(string='Désignation', required=True)
    ref_product_client = fields.Char(string='Référence Client', required=True)
