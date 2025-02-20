
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    force_invoiced = fields.Boolean(
        string="Force Facturation",
        help="Lorsque vous définissez ce champ, la commande client sera considérée comme "
         "entièrement facturé, même s'il peut y avoir commande ou livraison"
         "quantités en attente de facturation.",
        readonly=True,
        states={"done": [("readonly", False)], "fait": [("readonly", False)], "sale": [("readonly", False)]},
        copy=False,
    )

    @api.depends("force_invoiced")
    def _get_invoice_status(self):
        super(SaleOrder, self)._get_invoice_status()
        for order in self.filtered(
            lambda so: so.force_invoiced and so.state in ("sale", "done")
        ):
            order.invoice_status = "invoiced"