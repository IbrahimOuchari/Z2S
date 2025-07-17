import logging
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(string="Quantité trackée", default=0.0)
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

    qty_not_consumed = fields.Float(
        string="Quantité non consommée",
        store=True,
        help="Quantité livrée moins quantité nécessaire"
    )
    qty_total_updated = fields.Integer(string='Quantité totale mise à jour', default=False)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking_ids',
        string='Transferts liés à cet OF',
        store=True
    )
    ignore_component_check = fields.Boolean(string="Ignorer la vérification des composants")
    last_backorder_count = fields.Integer(string="Last Backorder Count", default=0)
    stock_move_changes = fields.Integer(string="Last Backorder Count", default=0)
    has_qty_delivered = fields.Integer(string="Last Backorder Count", default=0)
    has_qty_left = fields.Integer(string="Last Backorder Count", default=0)
    qty_left_trigger = fields.Integer(string="Last Backorder Count", default=0)
    tracked_picking_done_ids_str = fields.Text(string="Historique des pickings done trackés")

    def dummy_button_qty_delivered(self):
        # Placeholder for future logic when 'Trackée' button is clicked
        return True

    def dummy_button_qty_left(self):
        # Placeholder for future logic when 'Restante' button is clicked
        return True

    qty_delivered_total = fields.Float(
        string="Total Quantity Delivered",
        compute='_compute_qty_delivered_total',
        store=True,
    )

    qty_left_total = fields.Float(
        string="Total Quantity Left",
        store=True,
    )

    def _update_qty_left(self):
        excluded_states = ['done', 'cancel']
        min_date = datetime(2025, 7, 1)
        for production in self:
            # ✅ Skip if created before July 1st, 2025
            if production.create_date and production.create_date < min_date:
                print(f"[MFG {production.name}] Skipped qty_left update: create_date < 2025-07-01")
                continue

            pending_pickings = production.picking_ids.filtered(lambda p: p.state not in excluded_states)
            if pending_pickings:
                latest_picking = pending_pickings.sorted(key=lambda p: p.id, reverse=True)[0]
                print(f"[MFG {production.name}] Latest pending picking: ID {latest_picking.id}")
            else:
                # fallback to latest done or cancel picking to keep qty_left stable
                done_cancel_pickings = production.picking_ids.filtered(lambda p: p.state in excluded_states)
                if done_cancel_pickings:
                    latest_picking = done_cancel_pickings.sorted(key=lambda p: p.id, reverse=True)[0]
                    print(f"[MFG {production.name}] Fallback to latest done/cancel picking: ID {latest_picking.id}")
                else:
                    latest_picking = None
                    print(f"[MFG {production.name}] No pickings found, resetting qty_left.")

            if latest_picking:
                # Create map of products that exist in the latest picking
                product_left_map = {
                    ml.product_id.id: ml.quantity_left or 0.0
                    for ml in latest_picking.move_lines
                }

                # Calculate total only from products in the latest picking
                total_left = sum(product_left_map.values())

                # Update qty_left only for products that exist in the latest picking
                # Preserve existing qty_left for products not in the latest picking
                for move in production.move_raw_ids:
                    if move.product_id.id in product_left_map:
                        # Update qty_left for products in the latest picking
                        move.qty_left = product_left_map[move.product_id.id]
                    # If product not in latest picking, keep existing qty_left value (no change)

                # Update total (this will only reflect products from latest picking)
                production.qty_left_total = total_left

                print(
                    f"[MFG {production.name}] update_qty_left: total_left={total_left}, updated_products={list(product_left_map.keys())}")

            else:
                # no picking found at all - reset everything
                production.qty_left_total = 0.0
                for move in production.move_raw_ids:
                    move.qty_left = 0.0

    @api.depends(
        'picking_ids',
        'picking_ids.move_lines',
        'picking_ids.move_lines.quantity_done',
        'picking_ids.state'
    )
    def _compute_qty_delivered_total(self):
        for production in self:
            done_pickings = production.picking_ids.filtered(lambda p: p.state == 'done')
            total_qty = 0.0
            product_delivered_map = {}

            for pick in done_pickings:
                for ml in pick.move_lines:
                    pid = ml.product_id.id
                    qty = ml.quantity_done or 0.0
                    product_delivered_map[pid] = product_delivered_map.get(pid, 0.0) + qty
                    total_qty += qty

            production.qty_delivered_total = total_qty

            for move in production.move_raw_ids:
                pid = move.product_id.id
                move.qty_delivered = product_delivered_map.get(pid, 0.0)

            # Call updated qty_left method with 'assigned' filter
            self._update_qty_left()

            print(
                f"[MFG {production.name}] _compute_qty_delivered_total: delivered={total_qty}, "
                f"delivered_map={product_delivered_map}, qty_left_total={production.qty_left_total}"
            )

    def _collect_validation_messages(self):
        _logger.info("=== _collect_validation_messages called ===")

        # Skip entirely if we're in the middle of our post‑update write pass
        if self.env.context.get('skip_mrp_validation'):
            _logger.info("Skipping validation due to context flag")
            return [], []

        blocking_msgs = []
        warning_msgs = []

        for move in self.move_raw_ids:
            product = move.product_id.display_name
            delivered = float(move.qty_delivered or 0.0)
            needed = float(move.qty_needed or 0.0)

            _logger.info(f"Processing {product}: delivered={delivered}, needed={needed}")

            # Skip if fully delivered
            if delivered >= needed:
                _logger.info(f"  -> OK: fully delivered ({delivered} >= {needed})")
                continue

            # Blocking if nothing delivered
            if delivered <= 0.0:
                _logger.info(f"  -> BLOCKING: nothing delivered")
                blocking_msgs.append(
                    f"❌ {product} : {delivered:.2f}/{needed:.2f} unités\n"
                    "   • Aucune collecte effectuée."
                )

            # Warning if partial delivery
            else:
                missing = needed - delivered
                _logger.info(f"  -> WARNING: partial delivery ({delivered} < {needed})")
                warning_msgs.append(
                    f"⚠️ {product} : {delivered:.2f}/{needed:.2f} unités\n"
                    f"   • Il manque {missing:.2f} unité(s)."
                )

        _logger.info(f"Final result: {len(blocking_msgs)} blocking, {len(warning_msgs)} warnings")
        return blocking_msgs, warning_msgs

    def button_mark_done(self):
        _logger.info("=== button_mark_done called ===")

        result = super(MrpProduction, self).button_mark_done()

        for mrp in self:
            if mrp.ignore_component_check:
                continue

            # 1) Run normal validation
            _logger.info("Running validation...")
            blocking, warnings = mrp._collect_validation_messages()

            if blocking:
                _logger.info("Raising blocking error")
                raise UserError("❌ Erreurs de validation :\n\n" + "\n\n".join(blocking))
            if warnings:
                _logger.info("Raising warning error")
                raise UserError("ℹ️ Infos de validation :\n\n" + "\n\n".join(warnings))

            # 2) Update qty_needed_total and qty_not_consumed - only if no backorder wizard
            if mrp.state == 'done':  # Only if fully completed (no wizard shown)
                mrp._update_qty_totals()

        return result

    def _update_qty_totals(self):
        """Update qty_needed_total and qty_not_consumed after production completion"""
        for move in self.move_raw_ids:
            if move.qty_needed:
                old_total = move.qty_needed_total or 0.0
                move.qty_needed_total = old_total + move.qty_needed
                _logger.info(
                    f"✅ Updated {move.product_id.display_name}: qty_needed_total {old_total} + {move.qty_needed} = {move.qty_needed_total}"
                )

            if move.qty_delivered is not None and move.qty_needed_total is not None:
                old_not_consumed = move.qty_not_consumed or 0.0
                move.qty_not_consumed = max(move.qty_delivered - move.qty_needed_total, 0.0)
                _logger.info(
                    f"↺ Updated {move.product_id.display_name}: qty_not_consumed {old_not_consumed} -> {move.qty_not_consumed}"
                )

    def write(self, vals):
        result = super().write(vals)
        self.update_qty_needed_on_moves()

        if vals.get('state') == 'done':
            for mrp in self:
                mrp._update_qty_totals()

        return result

    mark_button_done = fields.Boolean()
    mark_button_done_counter = fields.Boolean()

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

    def action_return_components(self):
        self.ensure_one()
        # If nothing not-consumed (i.e. everything consumed), cancel immediately
        if all(move.qty_not_consumed <= 0.0 for move in self.move_raw_ids):
            self.state = 'cancel'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Pas de composants à retourner'),
                    'message': _(
                        'Tous les composants ont été entièrement consommés. '
                        'Il n\'y a pas de composants à retourner. '
                        'L\'état de la production est maintenant "Annulé".'
                    ),
                    'sticky': True,
                    'type': 'warning',
                }
            }
        # Otherwise, open the return wizard
        return {
            'name': _('Retour de composants'),
            'type': 'ir.actions.act_window',
            'res_model': 'return.components.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('nn_Z2S.view_return_components_wizard_form').id,
            'target': 'new',
            'context': {'default_mrp_production_id': self.id},
        }

    components_returned = fields.Boolean(
        string="Composants Retournés",
        store=True,
        default=False
    )
