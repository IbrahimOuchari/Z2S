from odoo import models, fields, api
from pkg_resources import require


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    location_dest_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
    )
    date_done = fields.Datetime('Date Transfère', copy=False, readonly=False, required=True,
                                help="Date à laquelle le transfert a été traité ou annulé.")

    def write(self, vals):
        # Store the previous quantity left for comparison
        previous_quantities = {}
        if 'move_lines' in vals:
            for move in self.move_lines:
                previous_quantities[move.id] = move.quantity_left

        # Call the original write method
        result = super(StockPicking, self).write(vals)

        # Check if quantity_left has changed
        for move in self.move_lines:
            new_quantity_left = move.quantity_left
            if move.id in previous_quantities and previous_quantities[move.id] != new_quantity_left:
                # Trigger the wizard's default_get method or perform your desired action
                self.env['return.components.wizard'].default_get([])

        return result

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for move in self.move_lines:
            if move.ref_of:
                for raw_move in move.ref_of.move_raw_ids:
                    total_done = sum(move.move_line_ids.mapped('qty_done'))
                    raw_move.quantity_left = raw_move.product_uom_qty - total_done
        return res
