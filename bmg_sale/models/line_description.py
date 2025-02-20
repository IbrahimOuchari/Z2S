from odoo import fields, models
from odoo import api, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_product_description_per_so_line = fields.Boolean(
        string="Autoriser l'utilisation uniquement de la description de vente du produit sur la commande client ",
        implied_group="bmg_sale."
                      "group_use_product_description_per_so_line",
        default=True,
    )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not self.product_id:  # pragma: no cover
            return res
        if (
                self.user_has_groups(
                    "bmg_sale."
                    "group_use_product_description_per_so_line"
                )
                and self.product_id.description_sale
        ):
            product = self.product_id
            if self.order_id.partner_id:
                product = product.with_context(
                    lang=self.order_id.partner_id.lang,
                )
            self.name = product.description_sale
        return res
