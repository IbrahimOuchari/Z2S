
from odoo import _, api, fields, models


class PaymentReport(models.TransientModel):
    _name = "account.payment.report"
    _description = "PaymentReport"

    date_from = fields.Date(string="Date Début", required=True, default=fields.Date.today)
    date_to = fields.Date(string="Date Fin", required=True, default=fields.Date.today)
    company_id = fields.Many2one("res.company", "Company", required=True, default=lambda self: self.env.user.company_id)
    journal_payment_ids = fields.Many2many(
        "account.journal", domain=[("type", "in", ["cash", "bank"])], string="Journal"
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PaymentReport, self).default_get(fields_list)
        journals = self.env["account.journal"].search([("type", "in", ["cash", "bank"])])
        res["journal_payment_ids"] = [(6, 0, journals.ids)]
        return res

    def do_compute(self):
        all_payments = self.env["account.payment"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("payment_type", "=", "inbound"),
                ("partner_type", "=", "customer"),
                ("state", "in", ["posted", "reconciled"]),
                ("journal_id", "in", self.journal_payment_ids.ids),
            ]
        )

        lines = []
        for payment in all_payments:
            values = {
                "report_id": self.id,
                "payment_date": payment.date,
                "partner_id": payment.partner_id.id,
                "amount": payment.amount,
                "currency_id": payment.currency_id.id,
                "payment_journal_id": payment.journal_id.id,
                "payment_method_id": payment.payment_method_id.id,
            }
            for invoice in payment.reconciled_invoice_ids:
                values["invoice_journal_id"] = invoice.journal_id.id
            lines += [values]

        self.env["account.payment.report.line"].create(lines)

    def button_show_report(self):
        self.do_compute()
        action = self.env.ref("bmg_account.action_account_payment_report_line").read()[0]
        action["display_name"] = "{} ({}-{})".format(
            action["name"],
            self.date_from,
            self.date_to,
        )
        action["domain"] = [("report_id", "=", self.id)]
        action["context"] = {
            "active_id": self.id,
            # "general_buttons": self.env["account.payment.report.line"].get_general_buttons(),
        }
        action["target"] = "main"
        return action

    def print_pdf(self):
        action_report = self.env.ref("bmg_account.action_account_payment_report_line")
        return action_report.report_action(self, config=False)


class PaymentReportLine(models.TransientModel):
    _name = "account.payment.report.line"
    _description = "PaymentReportLine"

    report_id = fields.Many2one("account.payment.report", string="Rapport")
    payment_date = fields.Date(string="Date")
    partner_id = fields.Many2one("res.partner", string="Client")
    amount = fields.Monetary(string="Montant", digits='Product Price')
    currency_id = fields.Many2one("res.currency", string="Devise")
    payment_journal_id = fields.Many2one("account.journal", string="Journal Paiement")
    payment_journal_type = fields.Selection(related="payment_journal_id.type", store=True)
    invoice_journal_id = fields.Many2one("account.journal", string="Journal des Factures")
    payment_method_id = fields.Many2one("account.payment.method", string="Méthode de Paiement")

    def get_general_buttons(self):
        return [
            {
                "action": "print_pdf",
                "name": _("Print Preview"),
                "model": "account.payment.report",
            }
        ]
