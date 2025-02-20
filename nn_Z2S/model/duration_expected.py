from odoo import models, fields, api


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    duration_expected = fields.Float(
        string='Durée Théorique',
        digits=(16, 2),
        compute='_compute_duration_expected',
        readonly=True,
        help="Expected duration (in minutes)"
    )
    duration_expected_formatted = fields.Char(
        string='Durée Théorique',
        compute='_compute_duration_expected_formatted',
        store=False,  # Not stored in the database
        help="Formatted expected duration in H M S"
    )


    @api.depends('production_id.bom_id.operation_ids', 'name')
    def _compute_duration_expected(self):
        for workorder in self:
            duration = 0.0
            if workorder.production_id and workorder.production_id.bom_id:
                # Find matching operations
                matching_operations = workorder.production_id.bom_id.operation_ids.filtered(
                    lambda op: op.name == workorder.name
                )
                # Handle multiple matches
                if matching_operations:
                    # Use the sum of all matching time cycles
                    duration = sum(matching_operations.mapped('time_cycle'))

            workorder.duration_expected = duration * workorder.operation_qty

    @api.depends('duration_expected')
    def _compute_duration_expected_formatted(self):
        for record in self:
            total_seconds = record.duration_expected * 60  # Convert minutes to seconds
            hours = int(total_seconds // 3600)  # Calculate hours
            minutes = int((total_seconds % 3600) // 60)  # Remaining minutes
            seconds = int(total_seconds % 60)  # Remaining seconds

            # Create the formatted string without zero values
            formatted_duration = []
            if hours > 0:
                formatted_duration.append(f"{hours}H")
            if minutes > 0 or hours > 0:  # Show minutes if there are hours or if minutes > 0
                formatted_duration.append(f"{minutes}M")
            if seconds > 0:  # Include seconds only if they are greater than zero
                formatted_duration.append(f"{seconds}S")

            # If no units are available, show "0S" as a default
            record.duration_expected_formatted = " ".join(formatted_duration) or "0S"
