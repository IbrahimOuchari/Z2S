# models/mrp_production_extension.py
import logging  # Optional: For logging, if you need to debug

from odoo import fields, models, _
from odoo.exceptions import UserError  # Important: Import UserError for custom error messages

_logger = logging.getLogger(__name__)  # Optional: Initialize logger


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Ensure these fields are defined in this model extension
    tq_created = fields.Boolean(
        string='TQ Créé',
        help="Indique si un enregistrement de Contrôle Qualité Tourney a été créé pour cet Ordre de Fabrication.",
        default=False
    )

    tourney_quality_id = fields.Many2one(
        'tourney.quality',
        ondelete='set null',  # You added this attribute
        string='Tournée Qualité Associé',
        store=True,
    )

    def button_redirect_tourney_quality(self):
        """
        Redirects to the associated Tourney Quality record.
        This method is called when the 'Contrôle Qualité' button is clicked.
        """
        self.ensure_one()  # Ensures the method operates on a single record.

        _logger.info(f"Attempting to redirect from MO {self.name} (ID: {self.id})")

        if not self.tourney_quality_id:
            _logger.warning(f"No quality_control_id found for MO {self.name}. tq_created: {self.tq_created}")
            raise UserError(_("Aucun enregistrement de Contrôle Qualité n'est associé à cet Ordre de Fabrication."))

        _logger.info(f"Redirecting to Tourney Quality record with ID: {self.quality_control_id.id}")

        return {
            'type': 'ir.actions.act_window',  # Specifies an action to open a window
            'name': _('Tournée Qualité'),  # Title of the window
            'res_model': 'tourney.quality',  # The model to open
            'view_mode': 'form',  # Open in form view
            'res_id': self.tourney_quality_id.id,  # The ID of the specific record to open
            'target': 'current',  # Open in the current tab/window (use 'new' for a popup)
        }
