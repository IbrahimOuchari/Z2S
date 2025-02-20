from odoo import models, api
from odoo.tools import config


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Fixe Prix d'achat quand les lignes de BC sont modifiées
    def _onchange_eval(self, field_name, onchange, result):
        ctx = self.env.context
        if field_name in {"product_qty", "product_uom"} and (
                not config["test_enable"]
                or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            cls = type(self)
            for method in self._onchange_methods.get(field_name, ()):
                if method == cls._onchange_quantity:
                    self._onchange_methods[field_name].remove(method)
                    break
        return super()._onchange_eval(field_name, onchange, result)

    # utilisation de la description seulement dans le BC Achat

    @api.onchange("product_id")
    def product_id_change(self):

        if self.product_id.description_purchase:
            product = self.product_id
            if self.order_id.partner_id:
                product = product.with_context(
                    lang=self.order_id.partner_id.lang,
                )
            self.name = product.description_purchase
