from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrderType(models.Model):
    _name = "purchase.order.type"
    _description = "Type of purchase order"
    _order = "sequence"

    @api.model
    def _get_domain_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return [
            ("code", "=", seq_type.code),
            ("company_id", "in", [False, self.env.company.id]),
        ]

    @api.model
    def _default_sequence_id(self):
        seq_type = self.env.ref("purchase.seq_purchase_order")
        return seq_type.id

    name = fields.Char(required=True, string="Nom")
    active = fields.Boolean(default=True)
    description = fields.Text(string="Description", translate=True)
    sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Séquence",
        copy=False,
        domain=lambda self: self._get_domain_sequence_id(),
        default=lambda self: self._default_sequence_id(),
        required=True,
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term", string="Modalités de Paiement"
    )
    incoterm_id = fields.Many2one(comodel_name="account.incoterms", string="Incoterm", invisible=1)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Société",
        default=lambda self: self.env.company,)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_type = fields.Many2one(
        comodel_name="purchase.order.type",
        readonly=False,
        string="Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super().onchange_partner_id()
        purchase_type = (
            self.partner_id.purchase_type
            or self.partner_id.commercial_partner_id.purchase_type
        )
        if purchase_type:
            self.order_type = purchase_type

    @api.onchange("order_type")
    def onchange_order_type(self):
        for order in self:
            if order.order_type.payment_term_id:
                order.payment_term_id = order.order_type.payment_term_id.id
            if order.order_type.incoterm_id:
                order.incoterm_id = order.order_type.incoterm_id.id

    @api.model
    def create(self, vals):
        if vals.get("name", "/") == "/" and vals.get("order_type"):
            purchase_type = self.env["purchase.order.type"].browse(vals["order_type"])
            if purchase_type.sequence_id:
                vals["name"] = purchase_type.sequence_id.next_by_id()
        return super().create(vals)

    @api.constrains("company_id")
    def _check_po_type_company(self):
        if self.filtered(
            lambda r: r.order_type.company_id
            and r.company_id
            and r.order_type.company_id != r.company_id
        ):
            raise ValidationError(_("Incompatibilité entre la société du document et la société du type"))

    def _default_order_type(self):
        return self.env["purchase.order.type"].search(
            [("company_id", "in", [False, self.company_id.id])],
            limit=1,
        )

    @api.onchange("company_id")
    def _onchange_company(self):
        self.order_type = self._default_order_type()

class PurchaseOrder(models.Model):
    _inherit = "purchase.rfq"

    order_type = fields.Many2one(
        comodel_name="purchase.order.type",
        readonly=False,
        string="Type",
        ondelete="restrict",
        domain="[('company_id', 'in', [False, company_id])]",
    )

class ResPartner(models.Model):
    _inherit = "res.partner"

    purchase_type = fields.Many2one(
        comodel_name="purchase.order.type", string="Type de Commande d'Achat"
    )
