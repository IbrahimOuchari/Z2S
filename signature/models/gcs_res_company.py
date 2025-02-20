from odoo import models, fields, api


# the below class is created for inheriting the res.company
class GcsCompany(models.Model):
    _inherit = 'res.company'

    signature = fields.Binary(string='Signature', store=True)
    check_liste_of = fields.Binary(string='Checklist de démarrage OF', store=True)
    log_afaq = fields.Binary(string='Logo AFAQ AFNOR', store=True)