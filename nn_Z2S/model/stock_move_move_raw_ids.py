import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(string="Quantité trackée", default=0.0)
    quantity_track = fields.Float(string="Quantité trackée")
    qty_left = fields.Float(string="Quantité restante", store=True)
    qty_needed = fields.Float(
        string="Quantité nécessaire",
        digits='Product Unit of Measure',
        readonly=True, store=True,
    )
    qty_needed_total = fields.Float(
        string="Total quantité nécessaire",
        digits='Product Unit of Measure',
        readonly=True, store=True,
        help="Sum of qty_needed for each product through all done pickings"
    )
    total_delivered = fields.Float(
        string="Total livré",
        default=0.0,
        help="Total quantity delivered across all pickings"
    )
    qty_consumed = fields.Float(
        string="Quantité consommée",
        default=0.0,
        help="Actual quantity consumed in this production"
    )
    qty_remaining_available = fields.Float(
        string="Quantité restante disponible",
        store=True,
        help="Quantity remaining available: total_delivered - qty_consumed"
    )


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking_ids',
        string='Transferts liés à cet OF',
        store=True
    )
    stock_move_changes = fields.Float(string="Déclencheur de suivi", compute="_compute_qty_delivered", store=True)
    ignore_component_check = fields.Boolean(string="Ignorer la vérification des composants")
    last_backorder_count = fields.Integer(string="Last Backorder Count", default=0)
    tracked_picking_done_ids_str = fields.Text(string="Historique des pickings done trackés")

    @api.depends('picking_ids.move_lines.quantity_done',
                 'picking_ids.state',
                 'picking_ids.move_lines.quantity_left',
                 'mrp_production_backorder_count')
    def _compute_qty_delivered(self):
        for production in self:
            tracked_ids = json.loads(production.tracked_picking_done_ids_str or "[]")
            backorder_changed = False

            # 1) Reset qty_delivered when backorder count changes, but flag it
            if hasattr(production, 'last_backorder_count') \
                    and production.mrp_production_backorder_count != production.last_backorder_count:
                backorder_changed = True
                for move in production.move_raw_ids:
                    move.qty_delivered = 0.0
                tracked_ids = []
                production.last_backorder_count = production.mrp_production_backorder_count

            # 2) If any picking is not done, zero qty_delivered and bail out
            if any(p.state != 'done' for p in production.picking_ids):
                for move in production.move_raw_ids:
                    move.qty_delivered = 0.0
                continue

            # 3) Remember old remaining so we can preserve it on backorder change
            old_remaining = {
                move.product_id.id: move.qty_remaining_available or 0.0
                for move in production.move_raw_ids
            }

            done_pickings = production.picking_ids.filtered(lambda p: p.state == 'done')
            prod_deliv = {}
            prod_total = {}
            prod_left = {}

            # 4) Accumulate delivered, total and latest left
            for pick in done_pickings:
                for ml in pick.move_lines:
                    pid = ml.product_id.id
                    qty = ml.quantity_done
                    prod_deliv[pid] = prod_deliv.get(pid, 0.0) + qty
                    prod_total[pid] = prod_total.get(pid, 0.0) + qty
                    prod_left[pid] = ml.quantity_left

            # 5) Write everything back
            for move in production.move_raw_ids:
                pid = move.product_id.id
                move.qty_delivered = prod_deliv.get(pid, 0.0)
                move.total_delivered = prod_total.get(pid, 0.0)
                move.qty_left = prod_left.get(pid, move.qty_left or 0.0)

                if backorder_changed:
                    # Preserve old remaining on backorder change
                    move.qty_remaining_available = old_remaining.get(pid, 0.0)
                else:
                    # Normal compute: qty_delivered - qty_needed, min 0
                    move.qty_remaining_available = max(
                        move.qty_delivered - (move.qty_needed or 0.0),
                        0.0
                    )

            # 6) Update tracked pickings so we only accumulate new ones next time
            production.tracked_picking_done_ids_str = json.dumps(
                list(set(tracked_ids + [p.id for p in done_pickings]))
            )

    def compute_qty_delivered_total(self):
        # Left empty per instruction
        return

    from odoo.exceptions import UserError

    class MrpProduction(models.Model):
        _inherit = 'mrp.production'

        def button_mark_done(self):
            for mrp in self:
                if mrp.ignore_component_check:
                    continue

                errors = []
                for move in mrp.move_raw_ids:
                    product = move.product_id.display_name
                    needed = move.qty_needed or 0.0
                    delivered = move.qty_delivered or 0.0
                    remaining = move.qty_remaining_available or 0.0
                    total_avail = delivered + remaining

                    # 1) Fully delivered?
                    if delivered >= needed:
                        continue

                    # 2) Nothing delivered at all
                    if total_avail <= 0:
                        errors.append(
                            f"❌ {product} : 0/{needed:.2f} unités\n"
                            f"   • Aucune collecte effectuée."
                        )
                    # 3) Partially available
                    elif total_avail < needed:
                        missing = needed - total_avail
                        errors.append(
                            f"⚠️ {product} : {total_avail:.2f}/{needed:.2f} unités\n"
                            f"   • Il manque {missing:.2f} unité(s)."
                        )

                if errors:
                    raise UserError(
                        "🚫 Impossible de terminer la production, composants insuffisants :\n\n"
                        + "\n\n".join(errors)
                    )

            # If no errors, proceed with the normal done action
            return super(MrpProduction, self).button_mark_done()

    def update_all_delivery_tracking(self):
        for production in self:
            production._compute_qty_needed_total()

    def write(self, vals):
        res = super().write(vals)
        self.update_qty_needed_on_moves()
        return res

    def update_qty_needed_on_moves(self):
        for mrp in self:
            if not mrp.bom_id:
                continue
            qty_reference = mrp.qty_producing if mrp.qty_producing else mrp.product_qty
            if not qty_reference:
                continue
            for move in mrp.move_raw_ids:
                bom_line = mrp.bom_id.bom_line_ids.filtered(lambda l: l.product_id.id == move.product_id.id)
                move.qty_needed = bom_line[0].product_qty * qty_reference if bom_line else 0.0

    @api.onchange('qty_producing', 'bom_id')
    def _onchange_qty_needed_preview(self):
        self.update_qty_needed_on_moves()
