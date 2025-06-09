from odoo import models, fields


class MaintenanceCurativeSparePart(models.Model):
    _name = 'maintenance.curative.spare.part'
    _description = 'Pièce de rechange - Maintenance curative'

    product_id = fields.Many2one(
        'product.template',
        string='Référence pièce de rechange',
        required=True
    )

    name = fields.Char(
        string='Désignation',
        related='product_id.name',
        store=True,
        readonly=True
    )

    quantity = fields.Float(
        string='Quantité',
        required=True,
        default=1.0
    )

    curative_id = fields.Many2one(
        'maintenance.curative',
        string='Intervention curative',
        ondelete='cascade'
    )
