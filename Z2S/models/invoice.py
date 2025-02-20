from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    bl = fields.Char('stock.picking', related='picking_ids.name')
    bc = fields.Char('stock.picking', related='picking_ids.origin')
    ref_client_id_invoice = fields.Char('stock.picking', related='picking_ids.ref_client_id')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    num_bl = fields.Char('account.move', related='move_id.bl')
    ref_product_id = fields.Char('product.template', related="product_id.ref_product_client")
    poste_id_invoice = fields.Char(related="move_line_ids.poste_id")
    move_type = fields.Selection(related="move_id.move_type")
