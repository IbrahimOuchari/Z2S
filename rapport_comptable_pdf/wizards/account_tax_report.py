from odoo import models


class AccountTaxReport(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.tax.report.wizard'
    _description = 'Tax Report'

    def _print_report(self, data):
        return self.env.ref('rapport_comptable_pdf.action_report_account_tax').report_action(self, data=data)
