from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Add a field to count the number of operations related to the current production
    operation_count_action_trigger = fields.Integer(
        string="Nombre d'opérations",
        compute="_compute_operation_count_new",
        store=True,
        readonly=True
    )

    # Add a boolean field to trigger computation
    action_trigger_operation_count = fields.Boolean(
        string="Déclencheur de comptage d'opérations",
        default=False
    )

    @api.depends('action_trigger_operation_count')
    def _compute_operation_count_new(self):
        """Count the number of operations related to this production order."""
        for record in self:
            if record.action_trigger_operation_count:
                # Count the number of operations related to the production
                operation_count = self.env['mrp.operation.of'].search_count([
                    ('production_id', '=', record.id)
                ])
                record.action_trigger_operation_count = operation_count

                # Trigger 'do_real_duration' for all workorders related to this production
                workorders = self.env['mrp.workorder'].search([('production_id', '=', record.id)])
                for workorder in workorders:
                    workorder.do_real_duration()  # Trigger the method
                    workorder.compute_productivity()  # Trigger the method

                    # Trigger the method

                # Reset the boolean field after computation
                record.action_trigger_operation_count = False

    def prod_cal(self):
        """Count the number of operations related to this production order."""
        for record in self:
            if record.action_trigger_operation_count:
                # Count the number of operations related to the production
                operation_count = self.env['mrp.operation.of'].search_count([
                    ('production_id', '=', record.id)
                ])
                record.action_trigger_operation_count = operation_count

                # Trigger 'do_real_duration' for all workorders related to this production
                workorders = self.env['mrp.workorder'].search([('production_id', '=', record.id)])
                for workorder in workorders:
                    workorder.do_real_duration()  # Trigger the method
                    workorder.calculate_productivity()  # Trigger the method

                    # Trigger the method

                # Reset the boolean field after computation
                record.action_trigger_operation_count = False

    def action_call_for_productivity(self):
        for rec in self:
            for worker in rec.workorder_ids:
                worker.calculate_productivity()  # Trigger the method
