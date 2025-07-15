from odoo import models, fields, api, _


class TourneyQualityOperationalLineReprise(models.Model):
    _name = 'tourney.quality.operational.line.reprise'
    _description = 'Operational Line Rework Type'

    name = fields.Char(string='Rework Name', required=True)
    description = fields.Text(string='Description')
