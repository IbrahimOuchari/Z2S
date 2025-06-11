from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MaintenanceCurativeSparePart(models.Model):
    _name = 'maintenance.curative.spare.part.demand'
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
        
    )

    curative_id = fields.Many2one(
        'maintenance.curative',
        string='Intervention curative',
        ondelete='cascade'
    )
    qty_available = fields.Float(related='product_id.qty_available')

    @api.constrains('quantity', 'qty_available')
    def _check_quantity(self):
        for rec in self:
            # Cas 1 : plus de stock disponible
            if rec.quantity > rec.qty_available:
                raise UserError(_(
                    "La quantité demandée pour le produit “%s” (%s) ne peut pas dépasser la quantité disponible (%s)."
                ) % (
                                    rec.product_id.display_name,
                                    rec.quantity,
                                    rec.qty_available
                                ))

            # Cas 2 : plus aucun stock
            if rec.qty_available == 0:
                raise UserError(_(
                    "Le produit “%s” n’est pas disponible en stock."
                ) % rec.product_id.display_name)
