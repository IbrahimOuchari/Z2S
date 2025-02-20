from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_uom_qty = fields.Float("Product Quantity")
    quantity_done = fields.Float("Quantity Done")
    quantity_left = fields.Float(
        string='Quantité Restante',
        compute='_compute_quantity_left',
        store=True,
        help="Quantité de produit restant à traiter."
    )

    ref_of = fields.Many2one('mrp.production', string='Reference OF')

    @api.depends('move_line_ids.qty_done')
    def _compute_quantity_left(self):
        for move in self:
            total_done = sum(move.move_line_ids.mapped('qty_done'))
            move.quantity_left = move.product_uom_qty - total_done

            # Update the corresponding move_raw_ids for the production order
            if move.ref_of:
                for raw_move in move.ref_of.move_raw_ids:
                    raw_move.quantity_left = raw_move.product_uom_qty - sum(raw_move.move_line_ids.mapped('qty_done'))

