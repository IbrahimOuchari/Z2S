from odoo import models, fields, api
from odoo.exceptions import UserError


class MrpBomCancelWizard(models.Model):
    _name = 'bom.cancel.wizard'

    invalidation_reason = fields.Text(string="Raison d'invalidation", required=True,
                                      help="Indiquer la raison de l'invalidation")

    bom_id = fields.Many2one('mrp.bom', string='Nomenclature', required=True)

    def confirm_reject_bom(self):
        self.ensure_one()
        if not self.bom_id:
            raise UserError("La Nomenclature n'est pas spécifié.")

        # update BoM fields
        self.bom_id.write({
            'bom_cancel': True,
            'state': 'rejected',
            'invalidation_reason': self.invalidation_reason,

        })
        # Log the rejection in the chatter
        self.bom_id.message_post(
            body=f"Nomenclature rejeté pour la raison suivante:{self.invalidation_reason} "
        )
        return {'type': 'ir.actions.act_window_close'}
