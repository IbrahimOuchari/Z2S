from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging

# Set up a logger
_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    category_id = fields.Many2one('product.category', string='Article Category')
    partner_id = fields.Many2one('res.partner', string='Client')
    is_produit_fini = fields.Boolean(string="Produit Fini")
    is_produit_achete = fields.Boolean(string="Produit Acheté")
    is_produit_fourni = fields.Boolean(string="Produit Fourni")

    def action_open_inventory_lines(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Inventory Lines'),
            'res_model': 'stock.inventory.line',
        }
        context = {
            'default_is_editable': True,
            'default_inventory_id': self.id,
            'default_company_id': self.company_id.id,
        }
        # Define domains and context
        domain = [
            ('inventory_id', '=', self.id),
            ('location_id.usage', 'in', ['internal', 'transit'])
        ]
        if self.location_ids:
            context['default_location_id'] = self.location_ids[0].id
            if len(self.location_ids) == 1:
                if not self.location_ids[0].child_ids:
                    context['readonly_location_id'] = True

        if self.is_produit_fini:
            domain.append(('product_id.sale_ok', '=', True))

        if self.is_produit_fourni:
            domain.append(('product_id.fourni', '=', True))

        if self.is_produit_achete:
            domain.append(('product_id.purchase_ok', '=', True))

        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))

        if self.partner_id:
            domain.append(('product_id.client_id.id', '=', self.partner_id.id))

        if self.product_ids:
            # no_create on product_id field
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree_no_product_create').id
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id
        else:
            # no product_ids => we're allowed to create new products in tree
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree').id

        action['context'] = context
        action['domain'] = domain
        return action
