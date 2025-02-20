from odoo import models, fields, api, _


class Reprise(models.Model):
    _name = 'reprise'
    _description = 'Reprise'

    name = fields.Char(string='Nom de la Reprise', required=True)
    description = fields.Text(string='Description')
