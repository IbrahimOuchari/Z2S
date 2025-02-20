from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    partner_id = fields.Many2one('res.partner', related="order_id.partner_id")
