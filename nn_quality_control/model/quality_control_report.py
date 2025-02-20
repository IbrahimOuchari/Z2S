from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging

# Configure logging
_logger = logging.getLogger(__name__)


class QualityControlReport(models.Model):
    _inherit = 'control.quality'




    def print_control_quality(self):
        # Ensure there is only one record to generate the report
        self.ensure_one()

        # Fetch the report from the identifier
        report = self.env.ref('nn_quality_control.action_template_quality_controle_print')

        # Generate the report for the associated Label Management records
        # You might want to filter the LabelManagement records related to this production order
        return report.report_action(self)

