import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    quality_control_id = fields.Many2one(
        'control.quality',
        string='Quality Control',
        store=True,
    )

    control_quality_created = fields.Boolean(
        string="Contrôle Qualité Créé",
        compute="_compute_control_quality_created",
        store=True
    )

    @api.depends('quality_control_id')
    def _compute_control_quality_created(self):
        for rec in self:
            has_cq = self.env['control.quality'].search_count([('of_id', '=', rec.id)]) > 0
            rec.control_quality_created = has_cq

    @api.constrains('quality_control_id')
    def _check_unique_control_quality(self):
        for rec in self:
            if rec.quality_control_id:
                cqs = self.env['control.quality'].search([('of_id', '=', rec.id)])
                count = len(cqs)
                if count > 1:
                    cq_list = "\n".join([f"- {cq.reference} (ID: {cq.id})" for cq in cqs])
                    raise ValidationError(
                        f"Un seul contrôle qualité peut être créé par ordre de fabrication.\n"
                        f"Contrôles qualité existants pour cet OF :\n{cq_list}"
                    )

    quality_control_checked = fields.Boolean(
        string="Contrôle Qualité Vérifié",
        default=False,  # Default value set to False
        store=True  # Store the field value to persist it in the database
    )
    ppm = fields.Float(related='quality_control_id.ppm', string="PPM", store=True, digits=(16, 3))
    ppm1 = fields.Float(related='quality_control_id.ppm1', string="PPM Contrôle Lampe Loupe", store=True,
                        digits=(16, 3))
    ppm2 = fields.Float(related='quality_control_id.ppm2', string="PPM Contrôle Caméra PPM", store=True, digits=(16, 3))
    ppm3 = fields.Float(related='quality_control_id.ppm3', string="PPM Contrôle Rayon X PPM", store=True,
                        digits=(16, 3))
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

    def action_view_control_quality(self):
        self.ensure_one()

        # If already created, prevent duplicate and inform the user
        if self.control_quality_created or self.quality_control_id:
            raise UserError(_("Un Contrôle Qualité existe déjà pour cet OF."))

        # Generate CQ reference
        current_year = fields.Date.today().strftime('%y')
        sequence = self.env['ir.sequence'].next_by_code('control.quality') or '0001'
        reference = f"CQ - {current_year} - {sequence}"

        # Create new Control Quality record
        new_cq = self.env['control.quality'].create({
            'of_id': self.id,
            'reference': reference,
            'client_id': self.client_id.id,
            'article_id': self.product_id.id,
            'client_reference': self.ref_product_client,
            'designation': self.description,
            'qty_producing': self.product_qty,
        })

        # Link and flag
        self.write({
            'quality_control_id': new_cq.id,
            'control_quality_created': True,
        })

        # Redirect to newly created CQ
        return {
            'name': 'Créer Contrôle Qualité',
            'type': 'ir.actions.act_window',
            'res_model': 'control.quality',
            'view_mode': 'form',
            'res_id': new_cq.id,
            'view_id': self.env.ref('nn_quality_control.view_quality_control_form').id,
            'target': 'self',
        }

    def button_redirect_control_quality(self):
        for record in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contrôle Qualité',
                'res_model': 'control.quality',
                'res_id': record.quality_control_id.id,
                'view_mode': 'form',
                'target': 'current',
                'view_id': self.env.ref('nn_quality_control.view_quality_control_form').id,
            }

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
