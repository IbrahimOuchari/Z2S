from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    quality_control_id = fields.Many2one(
        'control.quality',
        string='Quality Control',
        store=True,
    )

