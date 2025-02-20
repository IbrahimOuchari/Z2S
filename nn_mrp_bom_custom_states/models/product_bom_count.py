from odoo import models, fields, api


class ProductTemplateBomCount(models.Model):
    _inherit = 'product.template'

    def _compute_bom_count(self):
        for product in self:
            product.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', product.id),
                ('state', '=', 'done'),

            ])
class ProductProductBomCount(models.Model):
    _inherit = 'product.product'

    def _compute_bom_count(self):
        for product in self:
            product.bom_count = self.env['mrp.bom'].search_count([
                ('product_tmpl_id', '=', product.id),
                ('state', '=', 'done'),

            ])
