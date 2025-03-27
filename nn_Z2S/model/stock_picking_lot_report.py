from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

# Configure logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_cancel_forced(self):
        pass

    def action_delete_quants(self):
        """
        Directly delete stock quants created by this picking
        """
        for picking in self:
            # Ensure picking is in done state
            if picking.state != 'done':
                raise UserError(_("Only completed transfers can have quants deleted."))

            # Find all move lines for this picking
            move_lines = picking.move_line_ids

            # Search and delete corresponding quants
            quants_to_delete = self.env['stock.quant'].search([
                ('picking_id', '=', picking.id)
            ])

            if not quants_to_delete:
                # If no quants found directly by picking, try by product and location
                for move_line in move_lines:
                    quants_to_delete |= self.env['stock.quant'].search([
                        ('product_id', '=', move_line.product_id.id),
                        ('location_id', '=', move_line.location_dest_id.id),
                        ('quantity', '=', move_line.qty_done)
                    ])

            # Delete the quants
            if quants_to_delete:
                quants_to_delete.unlink()

                # Cancel all moves
                picking.move_lines._action_cancel()

                # Remove move lines
                picking.move_line_ids.unlink()

                # Set picking state to cancelled
                picking.state = 'cancel'

                # Post a message about quant deletion
                picking.message_post(body="Quants deleted. Transfer operation cancelled.")
            else:
                raise UserError(_("No corresponding quants found to delete."))

        return True

    # Relation to label.management (for managing lots related to stock moves)
    label_management = fields.Many2one('label.management', string="Label Management")

    def print_lot_etiquettes(self):
        """
        Print lot etiquettes for each stock move associated with this picking.
        """
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('nn_Z2S.action_template_lot_print')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

    def check_lots(self):
        for move in self.move_ids_without_package:
            # Check if there are any associated label.management records with lots for the stock.move
            if not move.lot_management_ids:
                raise UserError("Aucun lot n'est assigné pour le produit %s." % move.product_id.name)

        # If all moves have associated lots, display a confirmation or do further actions
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Vérification réussie',
                'message': 'Tous les mouvements ont des lots associés.',
                'type': 'success',
                'sticky': False,
            }
        }
