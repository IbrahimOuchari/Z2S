from odoo import models, _, fields
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

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

    def action_demand_close(self):
        for record in self:
            lines = record.get_filtered_inventory_lines()
            unconfirmed_lines = lines.filtered(lambda l: not l.value_confirmed)
            count_unconfirmed = len(unconfirmed_lines)

            if count_unconfirmed:
                message = _(
                    "Il y a %d ligne(s) non confirmée(s). Veuillez les confirmer avant de clôturer l'inventaire."
                ) % count_unconfirmed

                # First raise error with message
                raise UserError(message)

                # If you want to show the window, you can't do it after raising error in one call.
                # You would need to return the action instead of raising error, but then no popup message.

            # All confirmed
            record.state = 'demand_close'
