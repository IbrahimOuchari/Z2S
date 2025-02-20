from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    freeze_status = fields.Selection([
        ('full', 'Complètement Gelé'),
        ('partial', 'Partiellement Gelé'),
    ], string='Statut de Gel', copy=False)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_freeze = fields.Boolean(string='Est Gelé?', copy=False)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_start(self):
        res = super(StockInventory, self).action_start()
        for inventory in self:
            location_ids = self.env['stock.location'].search([
                ('id', 'child_of', inventory.location_ids.ids)
            ])
            if not location_ids:
                location_ids = self.env['stock.location'].search([
                    ('usage', '=', 'internal')
                ])
            product_ids = inventory.product_ids
            if not product_ids:
                product_ids = self.env['product.product'].search([])
            product_ids.write({'is_freeze': True})
            if not inventory.product_ids:
                location_ids.write({'freeze_status': 'full'})
            else:
                location_ids.write({'freeze_status': 'partial'})
        return res

    prepare_inventory = action_start

    def set_freeze_false(self):
        for inventory in self:
            location_ids = self.env['stock.location'].search([
                ('id', 'child_of', inventory.location_ids.ids)
            ])
            if not location_ids:
                location_ids = self.env['stock.location'].search([
                    ('usage', '=', 'internal')
                ])
            location_ids.write({'freeze_status': False})
            product_ids = inventory.product_ids
            if not product_ids:
                product_ids = self.env['product.product'].search([])
            product_ids.write({'is_freeze': False})

    def action_cancel_draft(self):
        res = super(StockInventory, self).action_cancel_draft()
        self.set_freeze_false()
        return res

    def _action_done(self):
        res = super(StockInventory, self)._action_done()
        self.set_freeze_false()
        return res


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        for me_id in self:
            if not me_id.move_id.inventory_id:
                if me_id.location_id.freeze_status == 'full':
                    raise UserError(
                        _("Impossible de déplacer le produit %s depuis l'emplacement %s, car l'emplacement est en statut gelé complet. Le mouvement de stock peut être traité après l'ajustement de l'inventaire.") % (
                            me_id.product_id.display_name, me_id.location_id.display_name))
                elif me_id.location_dest_id.freeze_status == 'full':
                    raise UserError(
                        _("Impossible de déplacer le produit %s vers l'emplacement %s, car l'emplacement est en statut gelé complet. Le mouvement de stock peut être traité après l'ajustement de l'inventaire.") % (
                            me_id.product_id.display_name, me_id.location_dest_id.display_name))
                elif me_id.location_id.freeze_status and me_id.product_id.is_freeze:
                    raise UserError(
                        _("Impossible de déplacer le produit %s depuis l'emplacement %s, car le produit et l'emplacement sont en statut gelé. Le mouvement de stock peut être traité après l'ajustement de l'inventaire.") % (
                            me_id.product_id.display_name, me_id.location_id.display_name))
                elif me_id.location_dest_id.freeze_status and me_id.product_id.is_freeze:
                    raise UserError(
                        _("Impossible de déplacer le produit %s vers l'emplacement %s, car le produit et l'emplacement sont en statut gelé. Le mouvement de stock peut être traité après l'ajustement de l'inventaire.") % (
                            me_id.product_id.display_name, me_id.location_dest_id.display_name))
        return super(StockMoveLine, self)._action_done()
