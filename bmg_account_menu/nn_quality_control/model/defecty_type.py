from odoo import models, fields, api, _


class DefectType(models.Model):
    _name = 'defect.type'
    _description = 'Type de Défaut'


    name = fields.Char(string='Nom du Défaut', required=True)
    description = fields.Text(string='Description')