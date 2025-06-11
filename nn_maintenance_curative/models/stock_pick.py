from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    maintenance_ids = fields.One2many(
        'maintenance.curative',
        'picking_id',
        string="Maintenances liées"
    )
