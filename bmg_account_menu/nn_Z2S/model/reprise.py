from odoo import models, fields, api, _


class RepriseType(models.Model):
    _name = 'reprise'
    _description = 'Type de Reprise'

    name = fields.Char(string='Nom du Type de Reprise', required=True)
