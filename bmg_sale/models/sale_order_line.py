from odoo import fields, models, api, _
from odoo.tools import config


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    #changer state dans sale order line
    state = fields.Selection(
        related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='brouillon')

    # Fixe Prix de vente quand les lignes de BC sont modifiées
    def _onchange_eval(self, field_name, onchange, result):
        ctx = self.env.context
        if field_name in {"product_uom_qty", "product_uom"} and (
                not config["test_enable"]
                or (config["test_enable"] and ctx.get("prevent_onchange_quantity", False))
        ):
            cls = type(self)
            for method in self._onchange_methods.get(field_name, ()):
                if method == cls.product_uom_change:
                    self._onchange_methods[field_name].remove(method)
                    break
        return super()._onchange_eval(field_name, onchange, result)
