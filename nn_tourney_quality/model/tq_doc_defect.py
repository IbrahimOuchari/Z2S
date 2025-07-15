from odoo import models, fields, api, _


class TourneyQualityDocumentaryLineDefect1(models.Model):
    _name = 'tourney.quality.documentary.line.defect1'
    _description = 'Documentary Line Defect Type 1'

    name = fields.Char(string='Defect Name', required=True)
    description = fields.Text(string='Description')
