from odoo import models, fields, api, _


class TourneyQualityDocumentaryLineReprise(models.Model):
    _name = 'tourney.quality.documentary.line.reprise'
    _description = 'Documentary Line Rework Type'

    name = fields.Char(string='Rework Name', required=True)
    description = fields.Text(string='Description')
