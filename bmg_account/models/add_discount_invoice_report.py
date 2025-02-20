from odoo import models, fields, api


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    invoice_discount = fields.Float('Remise', store=True)

    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        select = """
            ,line.discount as invoice_discount
         """
        select_str = res + select
        return select_str