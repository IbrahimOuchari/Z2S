from odoo import models, fields

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    # Adding fields to track corresponding fields from stock.inventory

    category_id = fields.Many2one('product.category', string='Article Category', related='product_id.categ_id', store=True)
    partner_id = fields.Many2one('res.partner', string='Client', related='product_id.client_id', store=True)
    client_id = fields.Many2one('res.partner', string='Client', related='product_id.client_id', store=True)
    is_produit_fini = fields.Boolean(string="Produit Fini", related='inventory_id.is_produit_fini', store=True)
    is_produit_achete = fields.Boolean(string="Produit Acheté", related='inventory_id.is_produit_achete', store=True)
    is_produit_fourni = fields.Boolean(string="Produit Fourni", related='inventory_id.is_produit_fourni', store=True)
