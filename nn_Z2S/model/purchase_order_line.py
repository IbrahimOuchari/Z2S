from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)




class StockOnHandRFQ(models.Model):
    _inherit = 'purchase.rfq.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_available_obj = self.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id),
                ('location_id.is_tracked_location', '=', True)  # Only count stock in tracked locations
            ])

            total_qty_available = sum(q.quantity for q in qty_available_obj)

            # Fetch the destruction quantity

            _logger.info('=================================================================')
            _logger.info('Total Qty Available for Product: %s, Product ID: %s, Available: %s, Destruction: %s',
                         rec.product_id.name, rec.product_id.id, total_qty_available,)
            _logger.info('=================================================================')

            # Set the available quantity, excluding the destruction
            rec.qty_available = total_qty_available


class StockLocationQuantityGet(models.Model):
    _inherit = 'stock.location'

    is_tracked_location = fields.Boolean(
        string="Inclure cette localisation dans le calcul du stock",
        help="Si activé, cette localisation sera prise en compte dans le calcul des quantités disponibles."
    )