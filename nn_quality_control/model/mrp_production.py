import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    quality_control_id = fields.Many2one(
        'control.quality',
        string='Quality Control',
        store=True,
    )

    quality_control_checked = fields.Boolean(
        string="Contrôle Qualité Vérifié",
        default=False,  # Default value set to False
        store=True  # Store the field value to persist it in the database
    )
    ppm = fields.Float(related='quality_control_id.ppm', string="PPM", store=True, digits=(16, 3))
    total_non_conform_count = fields.Integer(
        related='quality_control_id.total_non_conform_count',
        string='Total Nombre Non Conforme',
        store=True,
        digits=(16, 0),

    )
    global_defect_rate = fields.Float(
        related='quality_control_id.global_defect_rate',
        string='Taux Global des Défauts (%)',
        store=True,
        digits=(16, 0),

    )
    control_quality_state = fields.Selection(
        related='quality_control_id.state',
        store=True,
        readonly=True
    )

    # @api.onchange('quality_control_checked')
    # def _onchange_quality_control_checked(self):
    #     for record in self:
    #         if record.quality_control_checked:
    #             print("Function has started")
    #             _logger.info(f"Triggered _onchange_quality_control_checked for Record ID: {record.id}, Name: {record.name}")
    #
    #             control_count = self.env['control.quality'].search([
    #                 ('of_id', '=', record.name),
    #                 ('state', 'in', ['done', 'in_progress'])  # Include both 'done' and 'in_progress' states
    #             ])
    #
    #             _logger.info(
    #                 f"Search Results - Found ID: {control_count.id if control_count else 'Not Found'}, Name: {control_count.name if control_count else 'Not Found'}")
    #
    #             record.quality_control_id = control_count.id
    #             _logger.info(f"Updated Record {record.id} - quality_control_id set to {record.quality_control_id}")

    def action_update_control_quality(self):
        for record in self:
            if record.quality_control_checked:
                print("Function has started")
                _logger.info(
                    f"Triggered _onchange_quality_control_checked for Record ID: {record.id}, Name: {record.name}")

                control_count = self.env['control.quality'].search([
                    ('of_id', '=', record.id),
                ], limit=1)  # <- Fix here

                if control_count:
                    _logger.info(f"Search Results - Found ID: {control_count.id}, Name: {control_count.reference}")
                    record.quality_control_id = control_count.id
                    _logger.info(f"Updated Record {record.id} - quality_control_id set to {record.quality_control_id}")
                else:
                    _logger.warning(f"No quality control record found for Production ID {record.id}")
                    record.quality_control_id = False
            else:
                record.quality_control_id = False
                _logger.info(f"Cleared quality_control_id for Record {record.id}")

    def action_call_for_productivity(self):
        for record in self:
            if record.workorder_ids:
                record.workorder_ids.action_re_calculate_productivity()


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    def action_re_calculate_productivity(self):
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
