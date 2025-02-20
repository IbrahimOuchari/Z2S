from odoo import models, fields, api, _


class DefectType1(models.Model):
    _name = 'defect1.type'
    _description = 'Type de Défaut'

    name = fields.Char(string='Nom du Défaut', required=True)
    description = fields.Text(string='Description')


class DefectType2(models.Model):
    _name = 'defect2.type'
    _description = 'Type de Défaut'

    name = fields.Char(string='Nom du Défaut', required=True)
    description = fields.Text(string='Description')
