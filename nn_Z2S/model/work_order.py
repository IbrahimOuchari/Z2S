from unicodedata import digit

from odoo import models, fields, api
import logging
from datetime import timedelta, datetime

_logger = logging.getLogger(__name__)  # Logger setup


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    operation_count = fields.Integer(
        string="Operation Count",
        related='production_id.operation_count',  # Related to the operation_count field in mrp.production
        store=True,  # Store the related value in the database
        readonly=True  # Read-only as it's a related field
    )
    real_duration_float = fields.Float(string="Real Duration (in minutes)")
    operation_qty = fields.Float(string="Quantité")

    production_id = fields.Many2one('mrp.production', string="Production Order", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", related="production_id.product_id", store=True)
    duration_real = fields.Float(string="Real Duration", store=True)
    real_duration = fields.Float(string="Real Duration", store=True)
    real_duration_formatted = fields.Char(string="Formatted Duration", store=True)
    details_operation = fields.One2many('mrp.operation.of', 'workorder_id', string="Details Operations")
    productivity = fields.Float(string="Productivité", compute="_compute_productivity", store=True , digits=(16,3))
    productivity_display = fields.Char(string="Productivité (%)", compute="_compute_productivity_display")


    @api.depends('duration_expected_formatted', 'real_duration_formatted', 'operation_qty', 'details_operation')
    def _compute_productivity(self):
        for order in self:
            try:
                # Debugging output to see the actual values of the fields
                _logger.info(f"Calculating productivity for order {order.id}:")
                _logger.info(f"Duration Expected: {order.duration_expected}")
                _logger.info(f"Real Duration: {order.real_duration}")
                _logger.info(f"Duration Real: {order.duration_real}")
                _logger.info(f"Duration Real Float: {order.real_duration_float}")

                # Ensure the calculation is only done if linked to a production
                if order.production_id:
                    # Validate the fields are numbers and greater than 0
                    if order.duration_expected > 0 and order.real_duration_float > 0:
                        order.productivity = (order.duration_expected / order.real_duration_float)
                        _logger.info(f"Productivity calculated: {order.productivity}%")
                    else:
                        order.productivity = 0.0
                        _logger.warning(f"Productivity set to 0 due to invalid duration values for order {order.id}.")
                else:
                    order.productivity = 0.0  # Default value if no production is linked
                    _logger.warning(f"Productivity set to 0 because no production is linked to order {order.id}.")
            except Exception as e:
                _logger.error(f"Error calculating productivity for order {order.id}: {e}")
                order.productivity = 0.0

    @api.depends('productivity')
    def _compute_productivity_display(self):
        for order in self:
            if order.productivity is not None:
                order.productivity_display = f"{order.productivity}%"
            else:
                order.productivity_display = "0%"  # Handle the case when no productivity value is available
                order.productivity = 0.0

    def calculate_productivity(self):
        def _compute_productivity(self):
            for order in self:
                try:
                    # Debugging output to see the actual values of the fields
                    _logger.info(f"Calculating productivity for order {order.id}:")
                    _logger.info(f"Duration Expected: {order.duration_expected}")
                    _logger.info(f"Real Duration: {order.real_duration}")
                    _logger.info(f"Duration Real: {order.duration_real}")
                    _logger.info(f"Duration Real Float: {order.real_duration_float}")

                    # Ensure the calculation is only done if linked to a production
                    if order.production_id:
                        # Validate the fields are numbers and greater than 0
                        if order.duration_expected > 0 and order.real_duration_float > 0:
                            order.productivity = (order.duration_expected / order.real_duration_float)
                            _logger.info(f"Productivity calculated: {order.productivity}%")
                        else:
                            order.productivity = 0.0
                            _logger.warning(
                                f"Productivity set to 0 due to invalid duration values for order {order.id}.")
                    else:
                        order.productivity = 0.0  # Default value if no production is linked
                        _logger.warning(f"Productivity set to 0 because no production is linked to order {order.id}.")
                except Exception as e:
                    _logger.error(f"Error calculating productivity for order {order.id}: {e}")
                    order.productivity = 0.0
    def _extract_seconds_from_duration(self, duration_str):
        """
        Extract the total number of seconds from a formatted string (e.g., '1H 1M 1S')
        """
        total_seconds = 0

        if not duration_str:
            return total_seconds

        try:
            parts = duration_str.split()
            for part in parts:
                if 'H' in part:  # Hours
                    hours = int(part.replace('H', '').strip())
                    total_seconds += hours * 3600
                elif 'M' in part:  # Minutes
                    minutes = int(part.replace('M', '').strip())
                    total_seconds += minutes * 60
                elif 'S' in part:  # Seconds
                    seconds = int(part.replace('S', '').strip())
                    total_seconds += seconds
        except Exception as e:
            _logger.error(f"Erreur lors de l'extraction des secondes de la durée '{duration_str}': {e}")

        return total_seconds

    from datetime import timedelta  # Ensure to import necessary modules

    def do_real_duration(self):
        """Fetch real duration from heure_debut to heure_fin and handle proper time formatting with second rollover.
           Also, compute the total quantity (quantite) and store it in operation_qty.
        """
        for workorder in self:
            total_duration = timedelta(0)
            total_quantite = 0  # Initialize total quantity for operation_qty

            # Search for operations that match the workorder
            matching_operations = self.env['mrp.operation.of'].search([
                ('production_id.id', '=', workorder.production_id.id),
                ('operation.name', '=', workorder.name),
            ])

            # Calculate the total duration (in seconds) and sum the quantite
            for operation in matching_operations:
                if operation.heure_debut and operation.heure_fin:
                    # Ensure both times are datetime objects
                    if isinstance(operation.heure_debut, datetime) and isinstance(operation.heure_fin, datetime):
                        duration = operation.heure_fin - operation.heure_debut
                        total_duration += duration
                    else:
                        _logger.warning(
                            f"Invalid times for operation {operation.id}: Start: {operation.heure_debut}, End: {operation.heure_fin}")
                        continue  # Skip invalid operations

                    # Sum the quantite field
                    total_quantite += operation.quantite

            total_seconds = int(total_duration.total_seconds())

            # Properly handle minutes and seconds with rollover
            total_minutes = total_seconds // 60  # Integer division to get complete minutes
            remaining_seconds = total_seconds % 60  # Get remaining seconds

            # Handle durations that are less than one hour (i.e., display MM:SS format)
            if total_seconds == 0:
                formatted_duration = "Aucune Durée"
            else:
                hours = total_minutes // 60
                minutes = total_minutes % 60
                if hours > 0:
                    # Format durations over one hour as HH:MM:SS
                    formatted_duration = f"{hours}H {minutes:02d}M {remaining_seconds:02d}S"
                else:
                    # Format durations under one hour as MM:SS
                    formatted_duration = f"{minutes:02d}:{remaining_seconds:02d}"

            workorder.real_duration_formatted = formatted_duration

            _logger.info(f"Formatted duration for workorder {workorder.name}: {formatted_duration}")

            # Calculate real_duration_float properly (in minutes)
            if formatted_duration != "Aucune Durée":
                workorder.real_duration_float = total_minutes + (remaining_seconds / 60.0)
            else:
                workorder.real_duration_float = 0.0

            _logger.info(f"Real duration float for workorder {workorder.name}: {workorder.real_duration_float}")

            # Store the total quantite in operation_qty
            workorder.operation_qty = total_quantite

            _logger.info(f"Total quantity for workorder {workorder.name}: {total_quantite}")

    def _extract_duration_from_formatted(self, formatted_duration):
        """Extract total duration in minutes and seconds from a formatted duration string (e.g., '1H 1M 1S') and return as float."""
        total_minutes = 0
        total_seconds = 0

        # If the formatted duration is "Aucune Durée", return 0
        if formatted_duration == "Aucune Durée":
            return 0.0

        try:
            # Split the formatted duration string by spaces (H, M, S)
            parts = formatted_duration.split()
            for part in parts:
                if 'H' in part:  # Hours
                    hours = int(part.replace('H', '').strip())
                    total_minutes += hours * 60  # Convert hours to minutes
                elif 'M' in part:  # Minutes
                    minutes = int(part.replace('M', '').strip())
                    total_minutes += minutes  # Add minutes directly
                elif 'S' in part:  # Seconds
                    seconds = int(part.replace('S', '').strip())
                    total_seconds += seconds  # Add seconds directly
        except Exception as e:
            _logger.error(f"Error while extracting duration from '{formatted_duration}': {e}")

        # Convert total seconds into a decimal fraction of a minute
        total_minutes += total_seconds / 60.0
        return round(total_minutes, 2)  # Return the result as a float rounded to 2 decimal places


class MrpOperationOfCustom(models.Model):
    _inherit = 'mrp.operation.of'

    workorder_id = fields.Many2one('mrp.workorder', string="Work Order", ondelete='cascade')
    production_id = fields.Many2one('mrp.production', string="Production Order", ondelete='cascade')
    product_id = fields.Many2one('product.product', string="Product", ondelete='cascade')
    # Add a field to count the number of operations related to the current production


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # Add a field to count the number of operations related to the current production
    operation_count = fields.Integer(
        string="Operation Count",
        compute="_compute_operation_count",  # Computed field
        store=True,  # Store the computed value in the database for performance
        readonly=True  # Make it readonly since it's just a computed field
    )

    @api.depends('details_operation')  # Trigger computation when details_operation is updated
    def _compute_operation_count(self):
        """Count the number of operations related to this production order."""
        for record in self:
            # Count the number of mrp.operation.of records related to the current production_id
            operation_count = self.env['mrp.operation.of'].search_count([('production_id', '=', record.id)])
            record.operation_count = operation_count  # Set the count in the computed field

            # Now trigger the 'do_real_duration' method for all workorders related to this production
            workorders = self.env['mrp.workorder'].search([('production_id', '=', record.id)])
            for workorder in workorders:
                workorder.do_real_duration()  # Trigger real duration calculation for each workorder


    avg_productivity = fields.Float(
        string="Average Productivity",
        compute="_compute_avg_productivity",  # Computed field
        store=True,  # Store the computed value in the database
        readonly=True  # Make it readonly since it's just a computed field
    )

    @api.depends('workorder_ids')  # Trigger computation when workorder_ids are updated
    def _compute_avg_productivity(self):
        """Calculate the average productivity for all workorders related to this production."""
        for record in self:
            workorders = self.env['mrp.workorder'].search([('production_id', '=', record.id)])

            total_productivity = 0.0
            valid_workorders = 0  # To keep track of workorders that have valid productivity

            for workorder in workorders:
                if workorder.productivity:  # Check if productivity is already computed
                    total_productivity += workorder.productivity
                    valid_workorders += 1

            # Calculate the average productivity if there are valid workorders
            if valid_workorders > 0:
                record.avg_productivity = total_productivity / valid_workorders
            else:
                record.avg_productivity = 0.0
