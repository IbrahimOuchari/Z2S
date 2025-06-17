from odoo import models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    # def action_validate(self):
    #     if not self.exists():
    #         return
    #     self.ensure_one()
    #
    #     if not self.user_has_groups('stock.group_stock_manager'):
    #         raise UserError(_("Only a stock manager can validate an inventory adjustment."))
    #
    #     if self.state != 'demand_close':
    #         raise UserError(_(
    #             "You can't validate the inventory '%s', maybe this inventory "
    #             "has been already validated or isn't ready.", self.name))
    #
    #     # ✅ Modified inventory_lines filter:
    #     inventory_lines = self.line_ids.filtered(
    #         lambda l: (
    #                 l.product_id.tracking in ['lot', 'serial']
    #                 and not l.prod_lot_id
    #                 and (
    #                         l.theoretical_qty != l.product_qty
    #                         or (
    #                                 float_is_zero(l.product_qty, precision_rounding=l.product_uom_id.rounding)
    #                                 and l.confirmed_zero
    #                         )
    #                 )
    #         )
    #     )
    #
    #     # Standard filter for lines with serial + qty > 0 + lot set
    #     lines = self.line_ids.filtered(
    #         lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0
    #                   and l.product_id.tracking == 'serial'
    #                   and l.prod_lot_id
    #     )
    #
    #     if inventory_lines and not lines:
    #         wiz_lines = [(0, 0, {
    #             'product_id': product.id,
    #             'tracking': product.tracking
    #         }) for product in inventory_lines.mapped('product_id')]
    #
    #         wiz = self.env['stock.track.confirmation'].create({
    #             'inventory_id': self.id,
    #             'tracking_line_ids': wiz_lines
    #         })
    #
    #         return {
    #             'name': _('Tracked Products in Inventory Adjustment'),
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'views': [(False, 'form')],
    #             'res_model': 'stock.track.confirmation',
    #             'target': 'new',
    #             'res_id': wiz.id,
    #         }
    #
    #     # Custom logic: create stock moves for zero quantity lines with confirmed_zero
    #     # self._create_zero_confirmed_moves()
    #
    #     # Finalize the inventory
    #     self._action_done()
    #     self.line_ids._check_company()
    #     self._check_company()
    #     return True
    #
    # def _create_zero_confirmed_moves(self):
    #     """Generate stock moves for lines with 0 quantity and confirmed_zero = True."""
    #     self.ensure_one()
    #     StockMove = self.env['stock.move']
    #     move_vals = []
    #     lines_to_process = self.line_ids.filtered(lambda l: float_is_zero(
    #         l.difference_qty, precision_rounding=l.product_uom_id.rounding) and l.confirmed_zero)
    #
    #     for line in lines_to_process:
    #         virtual_location = line._get_virtual_location()
    #
    #         # Create the move with zero quantity to register it
    #         vals = line._get_move_values(
    #             0.0,  # quantity
    #             line.location_id.id,  # source
    #             virtual_location.id,  # destination
    #             True,
    #
    #         )
    #         move_vals.append(vals)
    #
    #     if move_vals:
    #         created_moves = StockMove.create(move_vals)
    #
    #         # Optional: link the moves back to the inventory line (if needed)
    #         # You can also update line state manually if necessary, like:
    #         for rec in created_moves:
    #             rec.state = 'done'

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'demand_close':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory "
                "has been already validated or isn't ready.", self.name))
        inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot',
                                                                                     'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
        lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1,
                                                               precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
        if inventory_lines and not lines:
            wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in
                         inventory_lines.mapped('product_id')]
            wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'res_id': wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True
