from odoo import fields, api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_quant_location_ids = fields.Many2many(
        'stock.location',
        compute='_compute_stock_quant_locations',
        string="Emplacements de stock", store=True
    )

    @api.depends('product_variant_ids.stock_quant_ids')
    def _compute_stock_quant_locations(self):
        for tmpl in self:
            tmpl.stock_quant_location_ids = self.env['stock.location'].search([
                ('id', 'in', self.env['stock.quant'].search([
                    ('product_id.product_tmpl_id', '=', tmpl.id)
                ]).mapped('location_id').ids)
            ])
