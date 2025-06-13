from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    numero_submission = fields.Char(string="Numéro de soumission")
    date_submission_start = fields.Date(string="Date de début de soumission")
    date_submission_end = fields.Date(string="Date de fin de soumission")
    date_submission = fields.Date(string="Date de soumission")  # Champ informatif

    @api.constrains('date_submission_start', 'date_submission_end')
    def _check_dates_validity(self):
        for rec in self:
            if rec.date_submission_start and rec.date_submission_end:
                if rec.date_submission_start > rec.date_submission_end:
                    raise UserError("La date de début ne peut pas être postérieure à la date de fin.")
            elif rec.date_submission_start or rec.date_submission_end:
                raise UserError("Veuillez remplir les deux dates : début et fin.")
