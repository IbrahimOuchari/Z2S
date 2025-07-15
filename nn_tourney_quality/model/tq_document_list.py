from odoo import models, fields, api, _


class TourneyQualityDocumentList(models.Model):
    _name = 'tourney.quality.document.list'
    _description = 'Quality Document List'

    name = fields.Char(string='Document Name', required=True, help="Name of the quality document type.")
    description = fields.Text(string='Description', help="Detailed description of this document type.")
    document_line_ids = fields.One2many(
        'tourney.quality.documentary.line',  # related model
        'quality_list_id',
        string='Operational Lines'
    )
