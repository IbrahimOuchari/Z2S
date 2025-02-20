from odoo import api, models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def product_id_change(self):

        if self.product_id.description_purchase:
            product = self.product_id
            if self.order_id.partner_id:
                product = product.with_context(
                    lang=self.order_id.partner_id.lang,
                )
            self.name = product.description_purchase

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    ref_product_client_id = fields.Char('product.template', related="product_id.ref_product_client")


class PurchaseRfqLine(models.Model):
    _inherit = "purchase.rfq.line"

    ref_product_client_id = fields.Char('product.template', related="product_id.ref_product_client")
