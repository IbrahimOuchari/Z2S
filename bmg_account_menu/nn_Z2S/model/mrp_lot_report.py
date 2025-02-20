from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

# Configure logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'



    label_management = fields.Many2one('label.management', string="Label Management")

    def print_etiquette(self):
        # Ensure there is only one record to generate the report
        self.ensure_one()

        # Fetch the report from the identifier
        report = self.env.ref('nn_Z2S.action_template_etiquette_print')

        # Generate the report for the associated Label Management records
        # You might want to filter the LabelManagement records related to this production order
        return report.report_action(self.mapped('label_management'))
