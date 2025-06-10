from odoo import models, api
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for picking in self:
            vente = picking.sale_id
            if vente and vente.date_submission_start and vente.date_submission_end:
                # Convert datetime to date
                done_date = picking.date_done.date() if picking.date_done else None
                if done_date and not (vente.date_submission_start <= done_date <= vente.date_submission_end):
                    raise ValidationError(
                        "Vous ne pouvez pas valider ce bon de livraison en dehors de la période de soumission définie dans la commande client.")
        return super(StockPicking, self).button_validate()
