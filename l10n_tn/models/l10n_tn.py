
from odoo import fields, models, api, _

class ChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journals = super(ChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        if company.country_id.code == "TN":
            for journal in journals:
                if journal['type'] in ['sale', 'purchase']:
                    journal['refund_sequence'] = True
        return journals
