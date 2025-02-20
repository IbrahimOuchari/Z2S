from odoo import models, fields, api
from odoo.exceptions import UserError


class WizardCancelInventory(models.TransientModel):
    _name = 'wizard.cancel.inventory'
    _description = 'Wizard to Reject Inventory'

    invalidation_reason = fields.Text(
        string="Raison d'invalidation",
        required=True,
        help="Indiquer la raison de l'invalidation"
    )
    inventory_id = fields.Many2one(
        'stock.inventory',
        string="Inventaire",
        required=True
    )

    def confirm_reject_inventory(self):
        """Handle rejection of inventory."""
        self.ensure_one()
        if not self.inventory_id:
            raise UserError("L'inventaire n'est pas spécifié.")

        # Update inventory fields
        self.inventory_id.write({
            'inventory_cancel': True,
            'state': 'confirm',
            'invalidation_reason': self.invalidation_reason,
        })

        # Log the rejection in the chatter
        self.inventory_id.message_post(
            body=f"Inventaire rejeté pour la raison suivante : {self.invalidation_reason}"
        )

        return {'type': 'ir.actions.act_window_close'}
