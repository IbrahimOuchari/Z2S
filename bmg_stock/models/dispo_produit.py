from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


# Ajouter la quantité disponible dans la ligne de commande

class stock_on_hand_purchase(models.Model):
    _inherit = 'purchase.order.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(qty.qty_available for qty in qty_available_obj)

            _logger.info('=================================================================')
            _logger.info(total_qty_available)
            _logger.info('=================================================================')

            rec.qty_available = total_qty_available


class stock_on_hand_purchase(models.Model):
    _inherit = 'purchase.rfq.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(qty.qty_available for qty in qty_available_obj)

            _logger.info('=================================================================')
            _logger.info(total_qty_available)
            _logger.info('=================================================================')

            rec.qty_available = total_qty_available


class stock_on_hand_sale(models.Model):
    _inherit = 'sale.order.line'

    qty_available = fields.Float(string='Qty en Stock', compute='_get_qty_available')

    @api.depends('product_id')
    def _get_qty_available(self):
        for rec in self:
            qty_line_obj = self.env['product.template']
            qty_available_obj = qty_line_obj.search([['name', '=', rec.product_id.name]])

            total_qty_available = sum(qty.qty_available for qty in qty_available_obj)

            _logger.info('=================================================================')
            _logger.info(total_qty_available)
            _logger.info('=================================================================')

            rec.qty_available = total_qty_available

