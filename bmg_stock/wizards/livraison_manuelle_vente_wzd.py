from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class ManualDelivery(models.TransientModel):
    _name = "manual.delivery"
    _description = "Manual Delivery"
    _order = "create_date desc"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # Get lines from active_model if it's a sale.order / sale.order.line
        sale_lines = self.env["sale.order.line"]
        active_model = self.env.context["active_model"]
        if active_model == "sale.order.line":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = self.env["sale.order.line"].browse(sale_ids)
        elif active_model == "sale.order":
            sale_ids = self.env.context["active_ids"] or []
            sale_lines = self.env["sale.order"].browse(sale_ids).mapped("order_line")
        if len(sale_lines.mapped("order_id.partner_id")) > 1:
            raise UserError(_("Veuillez sélectionner un partenaire à la fois"))
        if sale_lines:
            # Get partner from those lines
            partner = sale_lines.mapped("order_id.partner_id")
            res["partner_id"] = partner.id
            res["commercial_partner_id"] = partner.commercial_partner_id.id
            # Convert to manual.delivery.lines
            res["line_ids"] = [
                (
                    0,
                    0,
                    {
                        "order_line_id": line.id,
                        "name": line.name,
                        "product_id": line.product_id.id,
                        "qty_ordered": line.product_uom_qty,
                        "qty_procured": line.qty_procured,
                        "quantity": line.qty_to_procure,
                    },
                )
                for line in sale_lines
                if line.qty_to_procure and line.product_id.type != "service"
            ]
        return res

    commercial_partner_id = fields.Many2one(
        "res.partner", required=True, readonly=True, ondelete="cascade",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Adresse de Livraison",
        domain="""
            [
                "|",
                ("id", "=", commercial_partner_id),
                ("parent_id", "=", commercial_partner_id),
            ],
        """,
        ondelete="cascade",
    )
    carrier_id = fields.Many2one(
        "delivery.carrier", string="Méthode de Livraison", ondelete="cascade",
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Utiliser une Route Spécifique",
        domain=[("sale_selectable", "=", True)],
        ondelete="cascade",
        help="Laissez-le vide pour utiliser la même route que celui de la ligne de vente",
    )
    line_ids = fields.One2many(
        "manual.delivery.line", "manual_delivery_id", string="Lignes à Valider",
    )
    date_planned = fields.Datetime(string="Date Prévue")

    def confirm(self):
        """ Creates the manual procurements """
        self.ensure_one()
        sale_order_lines = self.line_ids.mapped("order_line_id")
        sale_order_lines.with_context(
            bmg_stock=self
        )._action_launch_stock_rule_manual()


class ManualDeliveryLine(models.TransientModel):
    _name = "manual.delivery.line"
    _description = "Manual Delivery Line"

    manual_delivery_id = fields.Many2one(
        "manual.delivery",
        string="Wizard",
        ondelete="cascade",
        required=True,
        readonly=True,
    )
    order_line_id = fields.Many2one(
        "sale.order.line",
        string="Lignes de Vente",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(related="order_line_id.product_id")
    name = fields.Text(related="order_line_id.name")
    qty_ordered = fields.Float(
        string="Commandée",
        related="order_line_id.product_uom_qty",
        help="Quantité commandée dans le bon de commande associé",
        readonly=True,
    )
    qty_procured = fields.Float(related="order_line_id.qty_procured")
    quantity = fields.Float()

    @api.constrains("quantity")
    def _check_quantity(self):
        """ Prevent delivering more than the ordered quantity """
        if any(
                float_compare(
                    line.quantity,
                    line.qty_ordered - line.qty_procured,
                    precision_rounding=line.product_id.uom_id.rounding,
                )
                > 0.00
                for line in self
        ):
            raise UserError(
                _(
                    "Vous ne pouvez pas livrer plus que la quantité restante. "
                    "Si vous devez le faire, veuillez d'abord modifier le bon de commande."
                )
            )
