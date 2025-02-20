from odoo import api, fields, models, _

from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ProductProductInventoryLine(models.Model):
    _inherit = 'product.product'

    def action_show_product_product_inventory_line(self):
        for record in self:
            # Search for inventory lines for the product and in 'done' state
            product_inventory_line_history = self.env['stock.inventory.line'].search([
                ('product_id', '=', record.id),
                ('state', '=', 'done')
            ], order='inventory_date asc')

            # Log the result of the search
            _logger.info('Inventory Line History for Product %s: %s', record.name, product_inventory_line_history)

            # If there are inventory lines, show them
            if product_inventory_line_history:
                return {
                    'name': _('Historique des ajustements d\'inventaire des produits pour ce produit'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.inventory.line',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('nn_Z2S.view_stock_inventory_line_tree_inherit_history').id,
                    'domain': [('id', 'in', product_inventory_line_history.ids)],
                    'target': 'current'
                }
            else:
                raise UserError(
                    _('Aucun ajustement d\'inventaire n\'a été effectué pour le produit "%s".') % record.name)


#keep these action i have no purpose for them except an error keeps poping up asking for them
    def action_confirm_product(self):
        for rec in self:
            rec.state_product = '1'

    def action_cancel_product(self):
        for rec in self:
            rec.produit_annule = True

        action = self.env.ref('Z2S.action_wizard_cancel_reason').read()[0]
        action['context'] = {
            'default_product_id': self.id,
        }
        return action

    def action_verif_product(self):
        for rec in self:
            rec.state_product = '2'

    def action_set_draft_product(self):
        for rec in self:
            rec.state_product = 'draft'

class ProductTemplateInventoryLine(models.Model):
    _inherit = 'product.template'

    def action_show_product_template_inventory_line(self):
        for record in self:
            # Search for inventory lines for the product and in 'done' state
            product_inventory_line_history = self.env['stock.inventory.line'].search([
                ('product_id', '=', record.id),
                ('state', '=', 'done')
            ], order='inventory_date asc')

            # Log the result of the search
            _logger.info('Inventory Line History for Product %s: %s', record.name, product_inventory_line_history)

            # If there are inventory lines, show them
            if product_inventory_line_history:
                return {
                    'name': _('Historique des ajustements d\'inventaire des produits pour ce produit'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.inventory.line',
                    'view_mode': 'tree',
                    'view_id': self.env.ref('nn_Z2S.view_stock_inventory_line_tree_inherit_history').id,
                    'domain': [('id', 'in', product_inventory_line_history.ids)],
                    'target': 'current'
                }
            else:
                raise UserError(
                    _('Aucun ajustement d\'inventaire n\'a été effectué pour le produit "%s".') % record.name)
