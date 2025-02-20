from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_date_due_payment_term = fields.Date(
        related="invoice_date_due", string="Date d'échéance Délai de paiement"
    )

    @api.onchange("invoice_date_due_payment_term")
    def _onchange_invoice_date_due_payment_term(self):
        """Propagate from Payment term due date to original field"""
        if self.invoice_date_due_payment_term:
            self.invoice_date_due = self.invoice_date_due_payment_term

    def _compute_amount(self):
        if self.env.context.get("bypass_compute_amount"):
            return
        return super()._compute_amount()

    def onchange(self, values, field_name, field_onchange):
        obj = self
        if field_name == "invoice_date_due" and self.state == "posted":
            obj = self.with_context(bypass_compute_amount=True)
        return super(AccountMove, obj).onchange(values, field_name, field_onchange)

    def write(self, vals):
        res = super().write(vals)
        if "invoice_date_due" in vals and self.state == "posted":
            payment_term_lines = self.line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                             in ("receivable", "payable")
            )
            payment_term_lines.write({"date_maturity": vals["invoice_date_due"]})
        return res
