from odoo import models, fields

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    ref_product_client_manual = fields.Char(string="Reference Articles étiquette", required=True)
