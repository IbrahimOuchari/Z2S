from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_origin = fields.Char(related="move_id.invoice_origin", string="Doc Source")
    invoice_date = fields.Date(related="move_id.invoice_date", string="Date Facturation")
    partner_ref = fields.Char(related="partner_id.ref", string="Référence Contact")
    payment_term_id = fields.Many2one(
        "account.payment.term",
        related="move_id.invoice_payment_term_id",
        string="Modalités de Paiement",
    )
    invoice_user_id = fields.Many2one(
        comodel_name="res.users",
        related="move_id.invoice_user_id",
        string="Vendeur",
        store=True,
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        model_data_obj = self.env["ir.model.data"]
        ids = model_data_obj.search(
            [("module", "=", "account_due_list"), ("name", "=", "view_payments_tree")]
        )
        if ids:
            view_payments_tree_id = model_data_obj.get_object_reference(
                "account_due_list", "view_payments_tree"
            )
        if ids and view_id == view_payments_tree_id[1]:
            # Use due list
            result = super(models.Model, self).fields_view_get(
                view_id, view_type, toolbar=toolbar, submenu=submenu
            )
        else:
            # Use special views for account.move.line object
            # (for ex. tree view contains user defined fields)
            result = super(AccountMoveLine, self).fields_view_get(
                view_id, view_type, toolbar=toolbar, submenu=submenu
            )
        return result
