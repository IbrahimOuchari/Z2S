import logging
from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class TourneyQuality(models.Model):
    _name = 'tourney.quality'
    _description = 'Tourney Quality Control'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Added for Odoo communication features
    _rec_name = 'name'  # Set _rec_name to 'name' for display purposes

    name = fields.Char(
        string='Reference',  # Renamed from 'reference' to 'name'
        required=True,
        readonly=True,
        copy=False,  # Prevent copying the name when duplicating records
        default=lambda self: _('New')
    )

    of_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        store=True,
        domain="[('control_quality_created', '=', False), ('state', 'in', ['confirmed','progress','to_close','done'])]",
        readonly=False, required=True,
    )
    of_selected = fields.Boolean(string="Sélectionné", compute='_compute_of_selected', store=True)

    @api.depends('of_id')
    def _compute_of_selected(self):
        for record in self:
            if record.of_id:
                record.of_selected = True
            else:
                record.of_selected = False

    def action_apply_of_to_lines(self):
        for tq in self:
            if tq.of_id:
                # Assuming 'quality_control_id' and 'control_quality_created' fields exist on mrp.production
                if not tq.of_id.quality_control_id:
                    tq.of_id.quality_control_id = tq.id
                if not tq.of_id.control_quality_created:
                    tq.of_id.control_quality_created = True

    def check_control_quality_by_wifi(self, wifi_id):
        cqs = self.env['tourney.quality'].search([('wifi_identifier', '=', wifi_id)])
        if not cqs:
            raise UserError(f"No Tourney Quality record found with WIFI-D {wifi_id}.")

        message = f"WIFI-D {wifi_id} is linked to the following Tourney Quality records:\n"
        for cq in cqs:
            message += f"  - Tourney Quality ID {cq.id} (Reference: {cq.name})\n"  # Changed reference to name

        raise UserError(message)

    @api.onchange('state', 'of_id', 'has_documentary_control', 'has_operational_control', 'has_product_control')
    def onchange_state_of_id(self):
        for record in self:
            _logger.info(
                f"Triggered onchange_state_ofid for Record ID: {record.id}, "
                f"State: {record.state}, "
                f"OF_ID: {record.of_id.id if record.of_id else 'None'}, "
                f"OF_Name: {record.of_id.name if record.of_id else 'None'}"
            )

            if not record.id or isinstance(record.id, models.NewId):
                _logger.info(f"Skipping onchange for unsaved record: {record.id}")
                return

            if not record.of_id:
                _logger.info("Skipping onchange - no OF_ID set")
                return

            # Note: The original code was interacting with 'quality_control_checked' and 'action_update_control_quality'
            # on mrp.production. These fields/methods would need to be added to the mrp.production model
            # for this part to function correctly in the new 'tourney.quality' context.
            if record.state in ['in_progress', 'validated', 'closed']:
                of_search = self.env['mrp.production'].search([('id', '=', record.of_id.id)])
                if of_search:
                    of_search.write({'quality_control_checked': True})
                    # of_search.action_update_control_quality() # Uncomment if this method exists on mrp.production
            else:
                of_search = self.env['mrp.production'].search([('id', '=', record.of_id.id)])
                if of_search:
                    of_search.write({'quality_control_checked': False})
                    # of_search.action_update_control_quality() # Uncomment if this method exists on mrp.production

                    _logger.info(
                        f"OF_Search Results - ID: {of_search.id if of_search else 'Not Found'}, "
                        f"Name: {of_search.name if of_search else 'Not Found'}, "
                        f"quality_control_checked: {of_search.quality_control_checked if of_search else 'Not Found'}"
                    )

    other_info = fields.Text(string="Other Info", default="RAS")

    controller_id = fields.Many2one('res.users', string='Controller', readonly=True,
                                    default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda
                                     self: self.env.company)  # Changed from res.users to res.company for clarity
    start_date = fields.Datetime(string='Start Date', compute='_compute_start_date', store=True)
    end_date = fields.Datetime(string='End Date', compute='_compute_end_date', store=True)
    manual_quantity = fields.Boolean(string='Manual Quantity', default=False)

    article_id = fields.Many2one('product.product', string='Article', store=True, compute='_compute_of_id')
    client_reference = fields.Char(string='Client Reference', store=True, compute='_compute_of_id')
    client_id = fields.Many2one('res.partner', string='Client', store=True, compute='_compute_of_id')

    designation = fields.Char(string='Designation', store=True, compute='_compute_of_id')

    qty_producing_related = fields.Float(related='of_id.qty_producing', string='Produced Quantity (MO)', store=True)
    product_qty_related = fields.Float(related='of_id.product_qty', string='Planned Quantity (MO)', store=True)
    state_of = fields.Selection(related='of_id.state', store=True)

    product_qty = fields.Float(string='Produced Quantity', store=True)

    has_documentary_control = fields.Boolean(string='Documentary Control', default=False)
    has_operational_control = fields.Boolean(string='Operational Control', default=False)
    has_product_control = fields.Boolean(string='Product Control', default=False)

    global_defect_rate = fields.Float(
        string='Global Defect Rate (%)',
        compute='_compute_global_defect_rate',
        store=True,
        digits=(16, 3),
    )

    @api.depends('documentary_non_conform_count', 'operational_non_conform_count', 'product_non_conform_count',
                 'total_documentary_lines', 'total_operational_lines', 'total_product_lines')
    def _compute_global_defect_rate(self):
        for record in self:
            total_non_conform = (record.documentary_non_conform_count +
                                 record.operational_non_conform_count +
                                 record.product_non_conform_count)
            total_lines = (record.total_documentary_lines +
                           record.total_operational_lines +
                           record.total_product_lines)

            if total_lines > 0:
                record.global_defect_rate = (total_non_conform / total_lines) * 100
            else:
                record.global_defect_rate = 0.0

    global_non_conforme = fields.Float(
        string='Total Non-Conform',
        store=True,
        digits=(16, 3),
    )

    documentary_line_ids = fields.One2many('tourney.quality.documentary.line', 'quality_id',
                                           string='Documentary Control Lines')
    operational_line_ids = fields.One2many('tourney.quality.operational.line', 'quality_id',
                                           string='Operational Control Lines')
    product_line_ids = fields.One2many('tourney.quality.product.line', 'quality_id',
                                       string='Product Control Lines')

    documentary_conform_count = fields.Integer(string='Conform Count',
                                               compute='_compute_conform_non_conform_documentary', store=True)
    documentary_non_conform_count = fields.Integer(string='Non-Conform Count',
                                                   compute='_compute_conform_non_conform_documentary', store=True)
    documentary_total_client_default = fields.Integer(string='Total Client Defect',
                                                      compute='_compute_conform_non_conform_documentary', store=True)
    documentary_client_default_avg = fields.Float(string='Client Defect Rate',
                                                  compute='_compute_defect_rate_documentary', store=True, digits=(6, 2))

    operational_conform_count = fields.Integer(string='Conform Count',
                                               compute='_compute_conform_non_conform_operational', store=True)
    operational_non_conform_count = fields.Integer(string='Non-Conform Count',
                                                   compute='_compute_conform_non_conform_operational', store=True)
    operational_total_client_default = fields.Integer(string='Total Client Defect',
                                                      compute='_compute_conform_non_conform_operational', store=True)
    operational_client_default_avg = fields.Float(string='Client Defect Rate',
                                                  compute='_compute_defect_rate_operational', digits=(6, 2), store=True)

    product_conform_count = fields.Integer(string='Conform Count', compute='_compute_conform_non_conform_product',
                                           store=True)
    product_non_conform_count = fields.Integer(string='Non-Conform Count',
                                               compute='_compute_conform_non_conform_product', store=True)
    product_total_client_default = fields.Integer(string='Total Client Defect',
                                                  compute='_compute_conform_non_conform_product', store=True)
    product_client_default_avg = fields.Float(string='Client Defect Rate', compute='_compute_defect_rate_product',
                                              store=True, digits=(6, 2))

    total_conform_count = fields.Integer(string='Total Conform Count', compute='_compute_total_conform_non_conform',
                                         store=True)
    total_non_conform_count = fields.Integer(string='Total Non-Conform Count',
                                             compute='_compute_total_conform_non_conform', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('validated', 'Validated'),
    ], string='Status', default='draft')

    @api.constrains('total_documentary_lines', 'total_operational_lines', 'total_product_lines', 'product_qty')
    def _check_total_lines_vs_product_qty(self):
        for record in self:
            if record.product_qty:  # Only apply if product_qty is set and not zero
                if record.has_documentary_control and record.total_documentary_lines > record.product_qty:
                    raise ValidationError(_(
                        "Total lines for Documentary Control (%s) exceeds the produced quantity (%s)."
                    ) % (record.total_documentary_lines, record.product_qty))

                if record.has_operational_control and record.total_operational_lines > record.product_qty:
                    raise ValidationError(_(
                        "Total lines for Operational Control (%s) exceeds the produced quantity (%s)."
                    ) % (record.total_operational_lines, record.product_qty))

                if record.has_product_control and record.total_product_lines > record.product_qty:
                    raise ValidationError(_(
                        "Total lines for Product Control (%s) exceeds the produced quantity (%s)."
                    ) % (record.total_product_lines, record.product_qty))

    ppm = fields.Float(string="PPM", compute="_compute_ppm", store=True, digits=(16, 3))
    ppm1 = fields.Float(string="PPM", store=True, digits=(16, 3))
    ppm2 = fields.Float(string="PPM", store=True, digits=(16, 3))
    ppm3 = fields.Float(string="PPM", store=True, digits=(16, 3))

    @api.depends('global_defect_rate', 'ppm_documentary', 'ppm_operational', 'ppm_product')
    def _compute_ppm(self):
        for record in self:
            ppm_values = []
            if record.has_documentary_control:
                ppm_values.append(record.ppm_documentary)
            if record.has_operational_control:
                ppm_values.append(record.ppm_operational)
            if record.has_product_control:
                ppm_values.append(record.ppm_product)

            if ppm_values:
                record.ppm = sum(ppm_values) / len(ppm_values)
            else:
                record.ppm = 0.0

    @api.onchange('total_lines', 'total_documentary_lines', 'total_operational_lines', 'total_product_lines',
                  'product_qty')
    def state_change(self):
        for record in self:
            _logger.info(
                f"Total Lines: {record.total_lines}, "
                f"Qty Producing: {record.product_qty}, "
                f"Total lines Documentary: {record.total_documentary_lines}, "
                f"Total lines Operational: {record.total_operational_lines}, "
                f"Total lines Product: {record.total_product_lines}, "
                f"Current State: {record.state}"
            )

            types_selected_count = 0
            all_selected_types_match_qty = True

            if record.has_documentary_control:
                types_selected_count += 1
                if record.total_documentary_lines != record.product_qty:
                    all_selected_types_match_qty = False

            if record.has_operational_control:
                types_selected_count += 1
                if record.total_operational_lines != record.product_qty:
                    all_selected_types_match_qty = False

            if record.has_product_control:
                types_selected_count += 1
                if record.total_product_lines != record.product_qty:
                    all_selected_types_match_qty = False

            if types_selected_count == 0:
                record.state = 'draft'
                _logger.info("State changed to draft - no control types selected")
                continue

            if not all_selected_types_match_qty:
                record.state = 'in_progress'
                _logger.info("State changed to in_progress - quantities don't match for selected types")
                continue

            record.state = 'closed'
            _logger.info("State changed to closed - all quantities match for selected types")

    total_lines = fields.Integer(string='Total Lines', compute='_compute_total_lines', readonly=True,
                                 store=True)  # Added store=True for total_lines
    total_documentary_lines = fields.Integer(string='Total Documentary Lines',
                                             compute='_compute_total_lines_documentary', store=True)
    total_operational_lines = fields.Integer(string='Total Operational Lines',
                                             compute='_compute_total_lines_operational', store=True)
    total_product_lines = fields.Integer(string='Total Product Lines', compute='_compute_total_lines_product',
                                         store=True)
    forced_closure = fields.Boolean(string='Forced Closure', default=False)

    @api.depends('documentary_line_ids', 'operational_line_ids', 'product_line_ids', 'has_documentary_control',
                 'has_operational_control', 'has_product_control')
    def _compute_total_lines(self):
        for record in self:
            total_lines_count = 0
            if record.has_documentary_control:
                total_lines_count += len(record.documentary_line_ids)
            if record.has_operational_control:
                total_lines_count += len(record.operational_line_ids)
            if record.has_product_control:
                total_lines_count += len(record.product_line_ids)
            record.total_lines = total_lines_count

    def action_cal_total_lines(self):
        for record in self:
            record._compute_total_lines()

    @api.depends('documentary_line_ids')
    def _compute_total_lines_documentary(self):
        for record in self:
            record.total_documentary_lines = len(record.documentary_line_ids)

    @api.depends('operational_line_ids')
    def _compute_total_lines_operational(self):
        for record in self:
            record.total_operational_lines = len(record.operational_line_ids)

    @api.depends('product_line_ids')
    def _compute_total_lines_product(self):
        for record in self:
            record.total_product_lines = len(record.product_line_ids)

    def action_validate(self):
        for record in self:
            if record.forced_closure:
                record.state = 'validated'
                continue  # Skip further checks if forced closure is active

            if record.has_documentary_control and record.total_documentary_lines != record.product_qty:
                raise ValidationError(  # Changed exceptions.ValidationError to ValidationError
                    "Validation Error: Total Documentary Control lines must match the produced quantity."
                )
            if record.has_operational_control and record.total_operational_lines != record.product_qty:
                raise ValidationError(  # Changed exceptions.ValidationError to ValidationError
                    "Validation Error: Total Operational Control lines must match the produced quantity."
                )
            if record.has_product_control and record.total_product_lines != record.product_qty:
                raise ValidationError(  # Changed exceptions.ValidationError to ValidationError
                    "Validation Error: Total Product Control lines must match the produced quantity."
                )

            record.state = 'validated'

    @api.onchange('documentary_line_ids', 'operational_line_ids', 'product_line_ids')
    def _onchange_set_start_date(self):
        for rec in self:
            if not rec.start_date and rec.total_lines > 0:
                rec.start_date = fields.Datetime.now()

    @api.onchange('documentary_line_ids', 'operational_line_ids', 'product_line_ids')
    def _compute_end_date(self):
        for record in self:
            # The original logic for end_date was based on total_lines.
            # This means end_date is updated every time a line is added or removed.
            # If you want it to be set only once when all checks are done and state is 'closed' or 'validated',
            # you might need to adjust this logic. For now, it mirrors the original.
            if record.total_lines > 0 and record.state in ['closed',
                                                           'validated']:  # Only set end date if there are lines and in a final state
                record.end_date = datetime.now()
            elif record.total_lines == 0:  # Clear end_date if no lines
                record.end_date = False

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name}"  # Changed reference to name
            result.append((record.id, name))
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """ Create a sequence for the student model """
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (self.env['ir.sequence'].
                                next_by_code('tourney.quality'))
        record = super(TourneyQuality, self).create(vals_list)

        if record.of_id:
            record.of_id.write({
                'tq_created': True,
                'tourney_quality_id': record.id,
            })

        return record

    backup_of_id = fields.Many2one('mrp.production', string='MO (Backup)', invisible=True)

    @api.onchange('of_id')
    def _onchange_of_id(self):
        for record in self:
            if record.of_id:
                record.backup_of_id = record.of_id
            elif record.backup_of_id:
                record.of_id = record.backup_of_id

    @api.depends('of_id')
    def _compute_of_id(self):
        for record in self:
            if record.of_id:
                record.article_id = record.of_id.product_id.id
                record.client_reference = record.of_id.ref_product_client  # Assuming this field exists on mrp.production
                record.designation = record.of_id.description  # Assuming this field exists on mrp.production

                if not record.product_qty:
                    record.product_qty = record.of_id.product_qty

                if not record.original_product_qty:
                    record.original_product_qty = record.of_id.product_qty

                record.client_id = record.of_id.client_id.id  # Assuming client is linked via partner_id on mrp.production
            else:
                record.article_id = False
                record.client_reference = False
                record.designation = False
                record.product_qty = False  # Changed from qty_producing to product_qty as per your fields
                record.client_id = False

    @api.depends('documentary_line_ids.result1')
    def _compute_conform_non_conform_documentary(self):
        for record in self:
            conform_count = sum(1 for line in record.documentary_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.documentary_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.documentary_line_ids if line.result1 == 'client_default')
            record.documentary_conform_count = conform_count
            record.documentary_non_conform_count = non_conform_count
            record.documentary_total_client_default = total_client_default

    @api.depends('operational_line_ids.result1')
    def _compute_conform_non_conform_operational(self):
        for record in self:
            conform_count = sum(1 for line in record.operational_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.operational_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.operational_line_ids if line.result1 == 'client_default')
            record.operational_conform_count = conform_count
            record.operational_non_conform_count = non_conform_count
            record.operational_total_client_default = total_client_default

    @api.depends('product_line_ids.result1')
    def _compute_conform_non_conform_product(self):
        for record in self:
            conform_count = sum(1 for line in record.product_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.product_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.product_line_ids if line.result1 == 'client_default')
            record.product_conform_count = conform_count
            record.product_non_conform_count = non_conform_count
            record.product_total_client_default = total_client_default

    @api.depends('documentary_conform_count', 'documentary_non_conform_count',
                 'operational_conform_count', 'operational_non_conform_count',
                 'product_conform_count', 'product_non_conform_count')
    def _compute_total_conform_non_conform(self):
        for record in self:
            record.total_conform_count = (
                    record.documentary_conform_count +
                    record.operational_conform_count +
                    record.product_conform_count
            )
            record.total_non_conform_count = (
                    record.documentary_non_conform_count +
                    record.operational_non_conform_count +
                    record.product_non_conform_count
            )

    ppm_documentary = fields.Float(string="PPM Documentary Control", compute='_compute_ppm_documentary', digits=(16, 3))

    @api.depends('documentary_client_default_avg')
    def _compute_ppm_documentary(self):
        for rec in self:
            rec.ppm_documentary = rec.documentary_client_default_avg * 10000

    ppm_operational = fields.Float(string="PPM Operational Control", compute='_compute_ppm_operational', digits=(16, 3))

    @api.depends('operational_client_default_avg')
    def _compute_ppm_operational(self):
        for rec in self:
            rec.ppm_operational = rec.operational_client_default_avg * 10000

    ppm_product = fields.Float(string="PPM Product Control", compute='_compute_ppm_product', digits=(16, 3))

    @api.depends('product_client_default_avg')
    def _compute_ppm_product(self):
        for rec in self:
            rec.ppm_product = rec.product_client_default_avg * 10000

    @api.depends('documentary_non_conform_count', 'total_documentary_lines')
    def _compute_defect_rate_documentary(self):
        for record in self:
            total = record.total_documentary_lines
            non_conform = record.documentary_non_conform_count
            base = total - non_conform
            if base > 0:
                record.documentary_client_default_avg = (non_conform / base) * 100
            else:
                record.documentary_client_default_avg = 0.0

    @api.depends('operational_non_conform_count', 'total_operational_lines')
    def _compute_defect_rate_operational(self):
        for record in self:
            total = record.total_operational_lines
            non_conform = record.operational_non_conform_count
            base = total - non_conform
            if base > 0:
                record.operational_client_default_avg = (non_conform / base) * 100
            else:
                record.operational_client_default_avg = 0.0

    @api.depends('product_non_conform_count', 'total_product_lines')
    def _compute_defect_rate_product(self):
        for record in self:
            total = record.total_product_lines
            non_conform = record.product_non_conform_count
            base = total - non_conform
            if base > 0:
                record.product_client_default_avg = (non_conform / base) * 100
            else:
                record.product_client_default_avg = 0.0

    barcode = fields.Char(string="Barcode", compute="_compute_barcode", store=True)

    @api.depends('name')  # Changed 'reference' to 'name'
    def _compute_barcode(self):
        for record in self:
            record.barcode = record.name if record.name else ''  # Changed 'reference' to 'name'

    def action_force_closure(self):
        for record in self:
            record.state = 'closed'
            record.forced_closure = True

    original_product_qty = fields.Float(string='Original Quantity')
    product_qty_percentage = fields.Float(string='Quantity Percentage (%)', default=100.0)

    @api.onchange('manual_quantity', 'product_qty_percentage', 'original_product_qty')
    def _onchange_quantity_fields(self):
        for record in self:
            if record.manual_quantity and not record.original_product_qty:
                record.original_product_qty = record.product_qty

            if record.manual_quantity and record.original_product_qty:
                record.product_qty = record.original_product_qty * (record.product_qty_percentage / 100.0)

            if not record.manual_quantity and record.original_product_qty:
                record.product_qty = record.original_product_qty
                record.product_qty_percentage = 100.0

    def write(self, vals):
        for record in self:
            # Handle manual quantity percentage logic
            if 'product_qty_percentage' in vals and record.manual_quantity:
                percentage = vals.get('product_qty_percentage')
                if record.original_product_qty:
                    vals['product_qty'] = record.original_product_qty * (percentage / 100.0)

            if 'manual_quantity' in vals and vals['manual_quantity'] and not record.original_product_qty:
                vals['original_product_qty'] = record.product_qty

            if 'manual_quantity' in vals and not vals['manual_quantity'] and record.original_product_qty:
                vals['product_qty'] = record.original_product_qty
                vals['product_qty_percentage'] = 100.0

        # Call super to write the changes
        res = super(TourneyQuality, self).write(vals)

        # After writing, update related mrp.production record if exists
        for record in self:
            if record.of_id:
                record.of_id.write({
                    'tq_created': True,
                    'tourney_quality_id': record.id,
                })

        return res
