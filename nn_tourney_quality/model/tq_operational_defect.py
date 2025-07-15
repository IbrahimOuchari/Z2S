from odoo import models, fields, api, _


class TourneyQualityOperationalLineDefect1(models.Model):
    _name = 'tourney.quality.operational.line.defect1'
    _description = 'Operational Line Defect Type 1'

    name = fields.Char(string='Defect Name', required=True)
    description = fields.Text(string='Description')
