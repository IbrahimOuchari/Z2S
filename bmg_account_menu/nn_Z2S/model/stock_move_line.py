from odoo import models, fields


class StockMoveLineCustom(models.Model):
    _inherit = 'stock.move.line'

    category_id = fields.Many2one('product.category', string='Article Category')
    type_id = fields.Selection(
        selection=lambda self: self._get_product_type_selection(),
        string='Article Type',
        readonly=True
    )
    partner_id = fields.Many2one('res.partner', string='Client')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)

    def _get_product_type_selection(self):
        # Fetch the selection values for the type field from product.template
        return self.env['product.template']._fields['type'].selection
