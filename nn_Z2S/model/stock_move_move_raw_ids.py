import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    qty_delivered = fields.Float(string="Quantité tracké", default=False)
    quantity_track = fields.Float(string="Quantité tracké")
    qty_left = fields.Float(string="Quantité restante", store=True)
    qty_needed = fields.Float(
        string="Quantité nécessaire",
        digits='Product Unit of Measure',
        readonly=True, store=True,
    )


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picking_ids = fields.Many2many(
        'stock.picking', compute='_compute_picking_ids',
        string='Picking associated to this manufacturing order',
        store=True
    )
    stock_move_changes = fields.Float(string="Déclencheur de suivi", compute="_compute_qty_delivered", store=True)
    ignore_component_check = fields.Boolean(string="Ignorer la vérification des composants")

    @api.depends('picking_ids.move_lines.quantity_done', 'picking_ids.state', 'picking_ids.move_lines.quantity_left')
    def _compute_qty_delivered(self):
        for production in self:
            product_qty_done = {}
            product_qty_left = {}

            # Step 1: Find the latest picking by name
            latest_picking = None
            done_pickings = [p for p in production.picking_ids if p.state == 'done']
            if done_pickings:
                latest_picking = max(done_pickings, key=lambda p: p.date_done)

            # Step 2: Compute qty_delivered and qty_left from latest picking only
            if latest_picking:
                for move in latest_picking.move_lines:
                    if move.product_id:
                        product_qty_done[move.product_id.id] = move.quantity_done
                        product_qty_left[move.product_id.id] = move.quantity_left

            # Step 3: Assign to move_raw_ids
            for move in production.move_raw_ids:
                move.qty_delivered = product_qty_done.get(move.product_id.id, 0.0)
                move.qty_left = product_qty_left.get(move.product_id.id, 0.0)
            if production.state == 'done':
                for move in production.move_raw_ids:
                    move.qty_delivered = 0

    def button_mark_done(self):
        for mrp in self:
            if mrp.ignore_component_check:
                # Skip checks, just call original function for this record
                continue

            erreurs = []
            for move in mrp.move_raw_ids:
                produit = move.product_id.display_name
                qty_livree = move.qty_delivered
                qty_requise = move.qty_needed

                if qty_livree <= 0:
                    erreurs.append(
                        f"❌ {produit} : {qty_livree:.2f}/{qty_requise:.2f} unités\n"
                        "👉 Aucune collecte effectuée. Veuillez transférer le produit."
                    )
                elif qty_livree < qty_requise:
                    manque = qty_requise - qty_livree
                    erreurs.append(
                        f"⚠️ {produit} : {qty_livree:.2f}/{qty_requise:.2f} unités\n"
                        f"👉 Quantité incomplète. Il manque encore {manque:.2f} unités à transférer."
                    )

            if erreurs:
                message = (
                        "🚫 Impossible de terminer la production à cause des composants suivants :\n\n"
                        + "\n\n".join(erreurs)
                )
                raise UserError(message)

        # Finally call the original button_mark_done on all records
        return super(MrpProduction, self).button_mark_done()

    def write(self, vals):
        res = super().write(vals)
        self.update_qty_needed_on_moves()
        return res

    def update_qty_needed_on_moves(self):
        for mrp in self:
            if not mrp.bom_id:
                continue

            # Decide which quantity to use: qty_producing or product_qty
            qty_reference = mrp.qty_producing if mrp.qty_producing else mrp.product_qty

            if not qty_reference:
                continue

            for move in mrp.move_raw_ids:
                bom_line = mrp.bom_id.bom_line_ids.filtered(lambda l: l.product_id.id == move.product_id.id)
                if bom_line:
                    qty_needed = bom_line[0].product_qty * qty_reference
                else:
                    qty_needed = 0.0

                move.qty_needed = qty_needed

        @api.onchange('product_qty', 'bom_id')
        def _onchange_qty_needed_preview(self):
            self.update_qty_needed_on_moves()
