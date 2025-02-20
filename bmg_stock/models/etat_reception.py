from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_status = fields.Selection(selection=[
            ('nothing', 'Rien à Recevoir'), ('to_receive', 'En Attente'),
            ('partial', 'Réception Partielle'), ('received', 'Reçu'),
            ('processing', 'En Cours')
    ], string='Status de Réception', compute='_compute_delivery_status', store=True,
        readonly=True, copy=False, default='nothing')

    @api.depends('state', 'order_line.qty_received')
    def _compute_delivery_status(self):
        for rec in self:
            pickings = self.env['stock.picking'].search([
                ('purchase_id', '=', rec.id)])
            orderlines = rec.mapped('order_line')
            if not pickings and not orderlines.filtered(lambda x:x.product_id.type == 'service'):
                rec.delivery_status = 'nothing'
            elif all(o.qty_received == 0 for o in orderlines):
                rec.delivery_status = 'to_receive'
            elif orderlines.filtered(lambda x: x.qty_received < x.product_qty):
                rec.delivery_status = 'partial'
            elif all(o.qty_received == o.product_qty for o in orderlines):
                rec.delivery_status = 'received'
            elif any(p.state in ('waiting', 'confirmed') for p in pickings):
                rec.delivery_status = 'processing'
