from odoo import api, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_form_id = self.env.ref("stock.view_inventory_form").id
        xmlid = "stock.action_inventory_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "views": [(view_form_id, "form")],
                "view_mode": "form",
                "context": {
                    "default_product_ids": [(6, 0, self.product_variant_ids.ids)],
                    "default_name": _("%s : Ajustement de l'Inventaire") % self.display_name,
                },
            }
        )
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_update_quantity_on_inventory_adjustment(self):
        """Create an Inventory Adjustment instead of edit directly on quants"""
        self.ensure_one()
        view_form_id = self.env.ref("stock.view_inventory_form").id
        xmlid = "stock.action_inventory_form"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action.update(
            {
                "views": [(view_form_id, "form")],
                "view_mode": "form",
                "context": {
                    "default_product_ids": [(6, 0, [self.id])],
                    "default_name": _("%s : Ajustement de l'Inventaire") % self.display_name,
                },
            }
        )
        return action


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        action = super()._get_quants_action(domain=domain, extend=extend)
        action["view_id"] = self.env.ref("stock.view_stock_quant_tree").id
        # Enables form view in readonly list
        action.update(
            {
                "view_mode": "tree,form",
                "views": [
                    (action["view_id"], "list"),
                    (self.env.ref("stock.view_stock_quant_form").id, "form"),
                ],
            }
        )
        return action
