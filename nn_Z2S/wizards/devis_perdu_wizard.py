from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleDevissCancelWizard(models.Model):
    _name = 'devis.perdu.wizard'

    invalidation_reason = fields.Text(string="Raison d'invalidation", required=True,
                                      help="Indiquer la raison de l'invalidation")

    sale_devis_id = fields.Many2one('sale.devis', string='Devis', required=True)

    def confirm_reject_devis(self):
        self.ensure_one()
        if not self.sale_devis_id:
            raise UserError("La Devis n'est pas spécifié.")

        # update BoM fields
        self.sale_devis_id.write({
            'devis_cancel': True,
            'state': 'cancel',
            'invalidation_reason': self.invalidation_reason,

        })
        # Log the rejection in the chatter
        self.sale_devis_id.message_post(
            body=f"Devis Non Concrétisé pour la raison suivante:{self.invalidation_reason} "
        )
        return {'type': 'ir.actions.act_window_close'}
