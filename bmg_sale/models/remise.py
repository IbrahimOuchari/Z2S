from odoo import api, fields, models
from lxml import etree

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Affiche le montant de remise dans le récap BC Vente
    discount_total = fields.Monetary("Total Remise", compute='total_discount', digits='Product Price')

    @api.depends('order_line.product_uom_qty', 'order_line.price_unit', 'order_line.discount')
    def total_discount(self):
        for order in self:
            total_price = 0
            discount_amount = 0
            final_discount_amount = 0
            if order:
                for line in order.order_line:
                    if line:
                        total_price = line.product_uom_qty * line.price_unit
                        if total_price:
                            discount_amount = total_price - line.price_subtotal
                            if discount_amount:
                                final_discount_amount = final_discount_amount + discount_amount
                order.update({'discount_total': final_discount_amount})

    # Fin

    # Appliquer remise globale sur BC

    general_discount = fields.Float(
        string="Remise (%)",
        compute="_compute_general_discount",
        store=True,
        readonly=False,
        digits="Discount",
    )

    @api.depends("partner_id")
    def _compute_general_discount(self):
        for so in self:
            so.general_discount = so.partner_id.sale_discount

    @api.model
    def fields_view_get(
            self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form":
            order_xml = etree.XML(res["arch"])
            order_line_fields = order_xml.xpath("//field[@name='order_line']")
            if order_line_fields:
                order_line_field = order_line_fields[0]
                context = order_line_field.attrib.get("context", "{}").replace(
                    "{",
                    "{'default_discount': general_discount, ",
                    1,
                )
                order_line_field.attrib["context"] = context
                res["arch"] = etree.tostring(order_xml)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount = fields.Float(
        compute="_compute_discount",
        store=True,
        readonly=False,
    )

    @api.model
    def create(self, vals):

        """Appliquer une remise générale pour les lignes de commande client qui ne sont pas créées
         à partir de la vue du formulaire de commande de vente."""

        if "discount" not in vals and "order_id" in vals:
            sale_order = self.env["sale.order"].browse(vals["order_id"])
            if sale_order.general_discount:
                vals["discount"] = sale_order.general_discount
        return super().create(vals)

    @api.depends("order_id", "order_id.general_discount")
    def _compute_discount(self):
        if hasattr(super(), "_compute_discount"):
            super()._compute_discount()
        for line in self:
            line.discount = line.order_id.general_discount


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_discount = fields.Float(
        string="Remise Client",
        digits="Discount",
        company_dependent=True,
    )
