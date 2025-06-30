import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(string="Quantité tracké")
    quantity_track = fields.Float(string="Quantité tracké")


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking_ids',
        string='Picking associated to this manufacturing order',
        store=True
    )
    stock_move_changes = fields.Float(string="Déclencheur de suivi", compute="_compute_qty_delivered", store=True)

    @api.depends('picking_ids.move_lines.quantity_done')
    def _compute_qty_delivered(self):
        for production in self:

            product_qty_done = {}

            for picking in production.picking_ids.filtered(lambda p: p.state == 'done'):
                for move in picking.move_lines:
                    if move.product_id:
                        product_qty_done.setdefault(move.product_id.id, 0.0)
                        product_qty_done[move.product_id.id] += move.quantity_done

            for move in production.move_raw_ids:
                move.qty_delivered = product_qty_done.get(move.product_id.id, 0.0)

    def button_mark_done(self):
        for mrp in self:
            errors = []

            # Check if there are any pending pickings
            has_pending_picking = any(picking.state != 'done' for picking in mrp.picking_ids)

            for move in mrp.move_raw_ids:
                delivered = move.qty_delivered
                qty_tobe_consumed = move.product_uom_qty
                qty_consumed = move.quantity_done

                # Case 1: Nothing delivered at all
                if delivered <= 0 and has_pending_picking:
                    errors.append(
                        f"{move.product_id.display_name}: {delivered:.2f}/{qty_tobe_consumed:.2f} (aucune collecte effectuée)"
                    )

                # Case 2: Delivered less than consumed & still pickings in progress
                elif delivered < qty_consumed and has_pending_picking:
                    missing_qty = qty_consumed - delivered
                    errors.append(
                        f"{move.product_id.display_name}: {missing_qty:.2f}/{qty_consumed:.2f} "
                        f"(transfert partiel — veuillez terminer les opérations de transfert)"
                    )

            if errors:
                raise UserError(
                    "Impossible de terminer la production à cause des composants suivants :\n\n" +
                    "\n".join(errors)
                )

        return super(MrpProduction, self).button_mark_done()
