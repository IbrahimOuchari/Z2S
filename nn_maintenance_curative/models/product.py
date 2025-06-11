from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_sale = fields.Text(string='Désignation', required=True)
    ref_product_client = fields.Char(string='Référence Client', required=True)
    is_spare_part = fields.Boolean(string="Pièce de réchange", default=False)


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    is_spare_part = fields.Boolean(related='product_tmpl_id.is_spare_part', string="Pièce de réchange", readonly=False)
