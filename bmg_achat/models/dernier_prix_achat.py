
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        related="product_variant_ids.last_purchase_line_ids",
        string="Dernières Lignes de Bon de Commande",
    )
    last_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        compute="_compute_last_purchase_line_id",
        string="Dernières Lignes de Bon de Commande",
    )
    last_purchase_price = fields.Float(
        compute="_compute_last_purchase_line_id_info", string="Dernier Prix d'Achat"
    )
    last_purchase_date = fields.Datetime(
        compute="_compute_last_purchase_line_id_info", string="Dernière Date d'Achat"
    )
    last_purchase_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_last_purchase_line_id_info",
        string="Dernier Fournisseur",
    )
    last_purchase_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_last_purchase_line_id_info",
        string="Dernière Devise d'Achat",
    )
    show_last_purchase_price_currency = fields.Boolean(
        related="product_variant_ids.show_last_purchase_price_currency",
    )
    last_purchase_price_currency = fields.Float(
        string="Prix d'Achat de la Dernière Devise",
        related="product_variant_ids.last_purchase_price_currency",
        digits=0,
    )

    @api.depends("last_purchase_line_ids")
    def _compute_last_purchase_line_id(self):
        for item in self:
            item.last_purchase_line_id = fields.first(item.last_purchase_line_ids)

    @api.depends("last_purchase_line_id")
    def _compute_last_purchase_line_id_info(self):
        for item in self:
            item.last_purchase_price = item.last_purchase_line_id.price_unit
            item.last_purchase_date = item.last_purchase_line_id.date_order
            item.last_purchase_supplier_id = item.last_purchase_line_id.partner_id
            item.last_purchase_currency_id = item.last_purchase_line_id.currency_id

class ProductProduct(models.Model):
    _inherit = "product.product"

    last_purchase_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        domain=[("state", "in", ["purchase", "done"])],
        string="Dernières Lignes de Bon de Commande",
    )
    last_purchase_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        compute="_compute_last_purchase_line_id",
        string="Dernières Lignes de Bon de Commande",
    )
    last_purchase_price = fields.Float(
        compute="_compute_last_purchase_line_id_info", string="Dernier Prix d'Achat", digits='Product Price'
    )
    last_purchase_date = fields.Datetime(
        compute="_compute_last_purchase_line_id_info", string="Dernière Date d'Achat"
    )
    last_purchase_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_last_purchase_line_id_info",
        string="Dernier Fournisseur",
    )
    last_purchase_currency_id = fields.Many2one(
        comodel_name="res.currency",
        compute="_compute_last_purchase_line_id_info",
        string="Dernière Devise d'Achat",
    )
    show_last_purchase_price_currency = fields.Boolean(
        compute="_compute_show_last_purchase_price_currency",
    )
    last_purchase_price_currency = fields.Float(
        string="Prix d'Achat de la Dernière Devise",
        compute="_compute_last_purchase_price_currency",
        digits=0,
    )

    @api.depends("last_purchase_line_ids")
    def _compute_last_purchase_line_id(self):
        for item in self:
            item.last_purchase_line_id = fields.first(item.last_purchase_line_ids)

    @api.depends("last_purchase_line_id")
    def _compute_last_purchase_line_id_info(self):
        for item in self:
            item.last_purchase_price = item.last_purchase_line_id.price_unit
            item.last_purchase_date = item.last_purchase_line_id.date_order
            item.last_purchase_supplier_id = item.last_purchase_line_id.partner_id
            item.last_purchase_currency_id = item.last_purchase_line_id.currency_id

    @api.depends("last_purchase_line_id", "last_purchase_currency_id")
    def _compute_show_last_purchase_price_currency(self):
        for item in self:
            last_line = item.last_purchase_line_id
            item.show_last_purchase_price_currency = (
                last_line
                and item.last_purchase_currency_id
                and item.last_purchase_currency_id != last_line.company_id.currency_id
            )

    @api.depends(
        "last_purchase_line_id",
        "show_last_purchase_price_currency",
        "last_purchase_currency_id",
        "last_purchase_date",
    )
    def _compute_last_purchase_price_currency(self):
        for item in self:
            if item.show_last_purchase_price_currency:
                rates = item.last_purchase_currency_id._get_rates(
                    item.last_purchase_line_id.company_id, item.last_purchase_date
                )
                item.last_purchase_price_currency = rates.get(
                    item.last_purchase_currency_id.id
                )
            else:
                item.last_purchase_price_currency = 1
