from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    force_invoiced = fields.Boolean(
        string="Forcer Facturation",
        readonly=True,
        states={"done": [("readonly", False)], "purchase": [("readonly", False)]},
        copy=False,
        help="Lorsque vous définissez ce champ, le bon de commande sera "
         "considéré comme entièrement facturé, même s'il peut y avoir commande"
         "ou quantités livrées en attente de facturation. Pour utiliser ce champ, "
         "la commande doit être à l'état 'Verrouillé'",
    )

    @api.depends("force_invoiced")
    def _get_invoiced(self):
        super(PurchaseOrder, self)._get_invoiced()
        for order in self.filtered(
            lambda po: po.force_invoiced and po.invoice_status == "to invoice"
        ):
            order.invoice_status = "invoiced"
