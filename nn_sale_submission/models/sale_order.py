from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    numero_submission = fields.Char(string="Numéro de soumission")
    date_submission_start = fields.Date(string="Date de début de soumission")
    date_submission_end = fields.Date(string="Date de fin de soumission")
    date_submission = fields.Date(string="Date de soumission")  # Champ informatif
