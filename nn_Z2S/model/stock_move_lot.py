from odoo import models, fields, api
from odoo.exceptions import UserError
from wheel.metadata import requires_to_requires_dist


class StockMove(models.Model):
    _inherit = 'stock.move'

    quantity_per_batch = fields.Float(string='Quantité par Lot', digits=(16, 0))  # Ensure this field exists
    lot_management_ids = fields.Many2many('label.management', string='Lots Created')  # Ensure this field exists
    label_management_ids = fields.One2many('label.management', 'stock_move_id', string='Labels')

    def action_create_lots(self):
        """
        Create lots for the stock move based on the `quantity_done` and `quantity_per_batch`.
        """
        for move in self:
            qty_done = move.quantity_done
            qty_per_batch = move.quantity_per_batch

            # Validate quantities
            if qty_done <= 0:
                raise UserError("La quantité traitée doit être supérieure à zéro.")

            if qty_per_batch <= 0:
                raise UserError("La quantité par lot doit être supérieure à zéro.")

            # New validation: Check if qty_per_batch is greater than qty_done
            if qty_per_batch > qty_done:
                raise UserError("La quantité par lot ne peut pas être supérieure à la quantité traitée.")

            # Calculate the number of lots to create
            number_of_lots = int(qty_done // qty_per_batch)
            remainder = qty_done % qty_per_batch

            # Call the label management function to create lots
            for _ in range(number_of_lots):
                self.env['label.management'].create_lots_for_stock_move(move, qty_per_batch)

            # If there's any remainder, create an additional lot
            if remainder > 0:
                self.env['label.management'].create_lots_for_stock_move(move, remainder)

            # Link created lots to the stock move
            created_lots = self.env['label.management'].search([
                ('stock_move_id', '=', move.id)
            ])
            move.lot_management_ids = [(6, 0, created_lots.ids)]  # Assign the lots to the stock move

        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Move Operations',
            'res_model': 'stock.move',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('stock.view_stock_move_operations').id,
            'target': 'new',
        }