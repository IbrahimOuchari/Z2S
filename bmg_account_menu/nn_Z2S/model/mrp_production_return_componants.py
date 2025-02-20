from email.policy import default

from odoo import models, fields, api, _

import logging

from psycopg2.sql import DEFAULT

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    return_state = fields.Selection(
        selection=[
            ('non_solde', 'Annulation en cours'),
            ('solde', 'Annulation OF')
        ],
        string='État Retour',
        store=True,
        compute="_compute_return_state",
        readonly=False,
        default=False,  # Allow direct editing if necessary
    )

    @api.onchange('quantity_left_total')
    def return_state_check(self):
        for production in self:
            if production.quantity_left_total > 0:  # Check if greater than zero
                production.return_state = 'solde'
            else:
                production.return_state = 'non_solde'

    quantity_left_total = fields.Boolean(compute='_compute_quantity_left_total', string="No Quantity Left to Return")
    line_ids = fields.One2many('return.lines', 'production_id', string="Return Lines")  # Example for return lines
    production_id = fields.Many2one('mrp.production', string="Production Order", required=True)

    @api.depends('move_raw_ids')
    def _compute_quantity_left_total(self):
        for production in self:
            total_quantity_left = 0.0  # Initialize total quantity left

            _logger.info("Calculating quantities left for OF %s", production.name)

            for move in production.move_raw_ids:
                # Log details about each move
                _logger.info("Processing move: %s | Quantity to Produce: %s | Quantity Done: %s",
                             move.product_id.name, move.product_uom_qty, move.quantity_done)

                if move.product_uom_qty > move.quantity_done:
                    quantity_left = move.product_uom_qty - move.quantity_done
                    _logger.info("Quantity left for %s: %s", move.product_id.name, quantity_left)

                    # Search for stock moves that have been returned
                    stock_moves = self.env['stock.move'].search([
                        ('product_id', '=', move.product_id.id),
                        ('picking_id.origin', '=', production.name),
                        ('picking_id.state', '=', 'done')  # Only consider done pickings
                    ])

                    total_returned = sum(stock_moves.mapped('product_uom_qty'))
                    quantity_left -= total_returned

                    _logger.info("Total returned for %s: %s | Adjusted Quantity Left: %s",
                                 move.product_id.name, total_returned, quantity_left)

                    # Aggregate total quantity left
                    if quantity_left > 0:
                        total_quantity_left += quantity_left

                    # Update the quantity_left field for the move
                    move.quantity_left = quantity_left  # Update the field directly
                    _logger.info("Updated quantity left for %s: %s", move.product_id.name, quantity_left)
                else:
                    move.quantity_left = 0  # Set to zero if there is no quantity left to return

            # Set the boolean field: True if nothing left to return, False otherwise
            production.quantity_left_total = total_quantity_left == 0

            # Log the result for the production order
            if production.quantity_left_total:
                _logger.info("Aucune quantité restante à retourner pour l'OF %s", production.name)
            else:
                _logger.info("Quantité restante à retourner pour l'OF %s : %s", production.name, total_quantity_left)

            # Update the return lines
            if total_quantity_left > 0:
                lines_to_return = []
                for move in production.move_raw_ids:
                    if move.product_uom_qty > move.quantity_done:
                        quantity_left = move.product_uom_qty - move.quantity_done

                        # Search for stock moves that have been returned
                        stock_moves = self.env['stock.move'].search([
                            ('product_id', '=', move.product_id.id),
                            ('picking_id.origin', '=', production.name),
                            ('picking_id.state', '=', 'done')  # Only consider done pickings
                        ])

                        total_returned = sum(stock_moves.mapped('product_uom_qty'))
                        quantity_left -= total_returned

                        if quantity_left > 0:
                            # Append to return lines if there's still quantity left
                            lines_to_return.append((0, 0, {
                                'product_id': move.product_id.id,
                                'quantity': quantity_left,
                                'quantity_left': quantity_left,
                                'move_id': move.id,
                                'production_id': production.id  # Ensure production_id is set
                            }))
                            _logger.info("Adding return line for %s: %s", move.product_id.name, quantity_left)

                # Update the return lines
                production.line_ids = lines_to_return

            # Update the return_state based on total_quantity_left
            production.return_state = 'solde' if total_quantity_left == 0 else 'non_solde'
            _logger.info("Updated return state for OF %s: %s", production.name, production.return_state)

    @api.depends('move_raw_ids')
    def _compute_return_state(self):
        for production in self:
            production.return_state = 'solde' if production.quantity_left_total else 'non_solde'

    return_count_total = fields.Integer(string="Retour des Composants", compute="_compute_return_count_total")

    @api.depends('name')
    def _compute_return_count_total(self):
        for production in self:
            # Assigning the computed count to the correct field (return_count_total)
            production.return_count_total = self.env['stock.picking'].search_count([
                ('origin', '=', production.name),
                ('picking_type_id.sequence_code', '=', 'RT'),
            ])

    def action_view_total_return_operations(self):
        self.ensure_one()
        return {
            'name': 'Retour des Composants',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name), ('picking_type_id.sequence_code', '=', 'RT')],
            'type': 'ir.actions.act_window',
        }


