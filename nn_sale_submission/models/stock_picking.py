from odoo import models, api, fields
from odoo.exceptions import ValidationError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date_done = fields.Datetime(default=fields.Datetime.now)

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

    numero_submission = fields.Char(
        related='sale_id.numero_submission',
        string="Numéro de soumission",
        readonly=True,
        store=True
    )
    date_submission_start = fields.Date(
        related='sale_id.date_submission_start',
        string="Date de début de soumission",
        readonly=True,
        store=True
    )
    date_submission_end = fields.Date(
        related='sale_id.date_submission_end',
        string="Date de fin de soumission",
        readonly=True,
        store=True
    )
