from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockOnHandPurchase(models.Model):
    _inherit = 'purchase.order.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')
    qty_destruction = fields.Float(string='Qty in Destruction', compute='_get_qty_destruction')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(q.qty_available for q in qty_available_obj)

            # Fetch the destruction quantity
            total_qty_destruction = self._get_qty_destruction(rec.product_id.id)

            # Log the available quantity and the destruction quantity
            _logger.info('=================================================================')
            _logger.info('Total Qty Available for Product: %s, Product ID: %s, Available: %s, Destruction: %s',
                         rec.product_id.name, rec.product_id.id, total_qty_available, total_qty_destruction)
            _logger.info('=================================================================')

            # Set the available quantity, excluding the destruction
            rec.qty_available = total_qty_available - total_qty_destruction

    def _get_qty_destruction(self, product_id):
        """Fetch quantity from the Destruction location for the given product ID."""
        total_qty_destruction = 0.0

        # Get the "Destruction" location ID
        destruction_location = self.env['stock.location'].search([('name', '=', 'Destruction')], limit=1)

        if destruction_location:
            # Get all stock quants for the product from the "Destruction" location
            stock_quants = self.env['stock.quant'].search([
                ('product_id', '=', product_id),
                ('location_id', '=', destruction_location.id)  # Only include the destruction location
            ])

            total_qty_destruction = sum(q.quantity for q in stock_quants)  # Sum the quantities

        _logger.info('Total Qty in Destruction for Product: %s, Product ID: %s, Total: %s',
                     self.env['product.product'].browse(product_id).name, product_id, total_qty_destruction)

        return total_qty_destruction


class StockOnHandRFQ(models.Model):
    _inherit = 'purchase.rfq.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')
    qty_destruction = fields.Float(string='Qty in Destruction', compute='_get_qty_destruction')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(q.qty_available for q in qty_available_obj)

            # Fetch the destruction quantity
            total_qty_destruction = self._get_qty_destruction(rec.product_id.id)

            # Log the available quantity and the destruction quantity
            _logger.info('=================================================================')
            _logger.info('Total Qty Available for Product: %s, Product ID: %s, Available: %s, Destruction: %s',
                         rec.product_id.name, rec.product_id.id, total_qty_available, total_qty_destruction)
            _logger.info('=================================================================')

            # Set the available quantity, excluding the destruction
            rec.qty_available = total_qty_available - total_qty_destruction

    def _get_qty_destruction(self, product_id):
        """Fetch quantity from the Destruction location for the given product ID."""
        total_qty_destruction = 0.0

        # Get the "Destruction" location ID
        destruction_location = self.env['stock.location'].search([('name', '=', 'Destruction')], limit=1)

        if destruction_location:
            # Get all stock quants for the product from the "Destruction" location
            stock_quants = self.env['stock.quant'].search([
                ('product_id', '=', product_id),
                ('location_id', '=', destruction_location.id)  # Only include the destruction location
            ])

            total_qty_destruction = sum(q.quantity for q in stock_quants)  # Sum the quantities

        _logger.info('Total Qty in Destruction for Product: %s, Product ID: %s, Total: %s',
                     self.env['product.product'].browse(product_id).name, product_id, total_qty_destruction)

        return total_qty_destruction


class StockOnHandSale(models.Model):
    _inherit = 'sale.order.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')
    qty_destruction = fields.Float(string='Qty in Destruction', compute='_get_qty_destruction')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(q.qty_available for q in qty_available_obj)

            # Fetch the destruction quantity
            total_qty_destruction = self._get_qty_destruction(rec.product_id.id)

            # Log the available quantity and the destruction quantity
            _logger.info('=================================================================')
            _logger.info('Total Qty Available for Product: %s, Product ID: %s, Available: %s, Destruction: %s',
                         rec.product_id.name, rec.product_id.id, total_qty_available, total_qty_destruction)
            _logger.info('=================================================================')

            # Set the available quantity, excluding the destruction
            rec.qty_available = total_qty_available - total_qty_destruction

    def _get_qty_destruction(self, product_id):
        """Fetch quantity from the Destruction location for the given product ID."""
        total_qty_destruction = 0.0

        # Get the "Destruction" location ID
        destruction_location = self.env['stock.location'].search([('name', '=', 'Destruction')], limit=1)

        if destruction_location:
            # Get all stock quants for the product from the "Destruction" location
            stock_quants = self.env['stock.quant'].search([
                ('product_id', '=', product_id),
                ('location_id', '=', destruction_location.id)  # Only include the destruction location
            ])

            total_qty_destruction = sum(q.quantity for q in stock_quants)  # Sum the quantities

        _logger.info('Total Qty in Destruction for Product: %s, Product ID: %s, Total: %s',
                     self.env['product.product'].browse(product_id).name, product_id, total_qty_destruction)

        return total_qty_destruction
