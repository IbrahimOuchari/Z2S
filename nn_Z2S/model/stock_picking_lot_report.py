from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

# Configure logging
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
