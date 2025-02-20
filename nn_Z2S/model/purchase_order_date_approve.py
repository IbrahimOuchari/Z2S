from odoo import models, fields, api, _, exceptions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_approve = fields.Datetime(
        string='Date Commande',
        required=True,  # Make the field required
    )

    @api.constrains(
        'purchase_request_id')  # Assuming 'purchase_request_id' is the field linking to the purchase request
    def _check_single_purchase_order(self):
        for order in self:
            if order.purchase_request_id:
                existing_orders = self.search_count([
                    ('purchase_request_id', '=', order.purchase_request_id.id),
                    ('id', '!=', order.id)  # Exclude the current order
                ])
                if existing_orders > 0:
                    raise exceptions.ValidationError(
                        "Only one purchase order can be linked to each purchase request."
                    )
