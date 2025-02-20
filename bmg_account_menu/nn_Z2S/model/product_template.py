from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quantity_per_batch_default = fields.Float(
        string='Quantité par Lot',
        help="Quantité par défaut par lot pour cet article.", digits=(16, 0)
    )


