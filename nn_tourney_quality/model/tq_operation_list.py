from odoo import models, fields, api, _


class TourneyQualityOperationList(models.Model):
    _name = 'tourney.quality.operational.list'
    _description = 'Quality Operation List'

    name = fields.Char(string='Operation Name', required=True, help="Name of the quality operation type.")
    description = fields.Text(string='Description', help="Detailed description of this operation type.")
    operational_line_ids = fields.One2many(
        'tourney.quality.operational.line',  # related model
        'quality_list_id',  # inverse Many2one field name on operational.line
        string='Operational Lines'
    )
