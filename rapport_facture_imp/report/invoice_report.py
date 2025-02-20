
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class ReportInvoices(models.AbstractModel):
    _name = 'report.rapport_facture_imp.invoice_outstanding'
    _description = 'Outstanding Invoice Report'

    '''Find Outstanding invoices between the date and find total outstanding amount'''
    @api.model
    def _get_report_values(self, docids, data=None):
        active_model = self.env.context.get('active_model')
        docs = self.env[active_model].browse(self.env.context.get('active_id'))
        outstanding_invoice = []       
        invoices = self.env['account.move'].search([('invoice_date_due', '>=', docs.start_date),('invoice_date_due', '<=', docs.end_date),('move_type','=', 'out_invoice'),('state','=','posted')])
        if invoices:
            amount_due = 0
            for total_amount in invoices:
                amount_due += total_amount.amount_residual
            docs.total_amount_due = amount_due

            return {
                'docs': docs,
                'invoices': invoices,
            }
        else:
            raise UserError("Aucune Facture Impayée à Afficher")
