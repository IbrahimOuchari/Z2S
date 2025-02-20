
from odoo import api, fields, models, _

class InvoiceOutstanding(models.TransientModel):
    _name = "invoice.outstanding"
    _description = "Invoice Outstanding"

    start_date = fields.Date(string='De la date', required='1', help='select start date')
    end_date = fields.Date(string='Jusqu''à', required='1', help='select end date')
    total_amount_due = fields.Integer(string='Encours Total')

    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date'])[0])
        return self.env.ref('rapport_facture_imp.action_customer_invoice_outstanding').report_action(self, data=data, config=False)


