from unicodedata import digit

from odoo import models, fields, api, exceptions, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class QualityControl(models.Model):
    _name = 'control.quality'
    _description = 'Contrôle de Qualité'

    reference = fields.Char(
        string='Référence Fiche Contrôle',
        required=True,
        readonly=True,
        default=lambda self: _('Nouveau')
    )

    of_id = fields.Many2one(
        'mrp.production',
        string='Ordre de Fabrication',
        ondelete='set null',
        domain="[('quality_control_checked', '=', False), ('state', 'in',  ['confirmed','progress','to_close','done'])]"
    )

    @api.onchange('state', 'of_id', 'type_1', 'type_2', 'type_3')
    def onchange_state_of_id(self):
        for record in self:
            _logger.info(
                f"Triggered onchange_state_ofid for Record ID: {self.id}, State: {record.state}, OF_ID: {record.of_id.id if record.of_id else 'None'},OF_Name: {record.of_id.name if record.of_id else 'None'}")

            if record.state in ['in_progress', 'validated', 'closed']:
                of_search = self.env['mrp.production'].search([
                    ('id', '=', record.of_id.id)
                ])
                if of_search:
                    of_search.write({
                        'quality_control_checked': True,
                    })
                    of_search.action_update_control_quality()
            else:
                of_search = self.env['mrp.production'].search([
                    ('id', '=', record.of_id.id)
                ])
                of_search.write({
                    'quality_control_checked': False,
                })
                of_search.action_update_control_quality()

                _logger.info(
                    f"OF_Search Results - ID: {of_search.id if of_search else 'Not Found'}, Name: {of_search.name if of_search else 'Not Found'}, quality_control_checked: {of_search.quality_control_checked if of_search else 'Not Found'}")

    other_info = fields.Text(string="Autre Info", default="RAS")

    controlleur_id = fields.Many2one('res.users', string='Contrôleur', readonly=True,
                                     default=lambda self: self.env.user)
    company = fields.Many2one('res.users', string='Contrôleur', readonly=True,
                              default=lambda self: self.env.user)
    start_date = fields.Datetime(string='Date début', compute='_compute_start_date', store=True )
    end_date = fields.Datetime(string='Date fin', compute='_compute_end_date', store=True)
    manual_quantity = fields.Boolean(string='Quantité Manuelle', default=False)

    article_id = fields.Many2one('product.product', string='Article', store=True, compute='_compute_of_id')
    client_reference = fields.Char(string='Référence Client', store=True, compute='_compute_of_id')
    client_id = fields.Many2one('res.partner', string='Client', store=True, compute='_compute_of_id')

    designation = fields.Char(string='Désignation', store=True, compute='_compute_of_id')  # New field for designation

    qty_producing_related = fields.Float(related='of_id.qty_producing', string='Quantité Produite', store=True,
                                         )  # New field for quantity produced
    product_qty_related = fields.Float(related='of_id.product_qty', string='Quantité Produite',
                                         )  # New field for quantity produced
    product_qty = fields.Float(string='Quantité Produite',store=True  )  # New field for quantity produced


    qty_producing = fields.Float(string='Quantité Produite', store=True,
                                 compute='_compute_of_id')  # New field for quantity produced

    type_1 = fields.Boolean(string='Type 1', default=False)
    type_2 = fields.Boolean(string='Type 2', default=False)
    type_3 = fields.Boolean(string='Type 3', default=False)
    global_defect_rate = fields.Float(
        string='Taux Global des Défauts (%)',
        compute='_compute_global_defect_rate',
        store=True,
        digits=(16, 3),
    )

    @api.depends('type1_non_conform_count', 'type2_non_conform_count', 'type3_non_conform_count',
                 'total_lines_type1', 'total_lines_type2', 'total_lines_type3')
    def _compute_global_defect_rate(self):
        for record in self:
            total_non_conform = (record.type1_non_conform_count +
                                 record.type2_non_conform_count +
                                 record.type3_non_conform_count)
            total_lines = (record.total_lines_type1 +
                           record.total_lines_type2 +
                           record.total_lines_type3)

            if total_lines > 0:
                record.global_defect_rate = (total_non_conform / total_lines) * 100
            else:
                record.global_defect_rate = 0.0  # Avoid division by zero

    type1_line_ids = fields.One2many('control.quality.type1.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type1')
    type2_line_ids = fields.One2many('control.quality.type2.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type2')
    type3_line_ids = fields.One2many('control.quality.type3.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type3')

    type1_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type1',
                                         store=True)
    type1_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type1',
                                             store=True)
    type1_total_client_default = fields.Integer(string='Nombre Total défaut client',
                                                compute='_compute_conform_non_conform_type1',
                                                store=True)
    type1_client_default_avg = fields.Integer(string='Taux des défaut client',
                                              compute='_compute_defect_rate_type1',
                                              store=True)
    type2_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type2',
                                         store=True)
    type2_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type2',
                                             store=True)
    type2_total_client_default = fields.Integer(string='Nombre Total défaut client',
                                                compute='_compute_conform_non_conform_type2',
                                                store=True)
    type2_client_default_avg = fields.Integer(string='Taux des défaut client',
                                              compute='_compute_defect_rate_type2',
                                              store=True)

    type3_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type3',
                                         store=True)
    type3_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type3',
                                             store=True)
    type3_total_client_default = fields.Integer(string='Nombre Total défaut client',
                                                compute='_compute_conform_non_conform_type3',
                                                store=True)
    type3_client_default_avg = fields.Integer(string='Taux des défaut client',
                                              compute='_compute_defect_rate_type3',
                                              store=True)
    total_conform_count = fields.Integer(string='Total Nombre Conforme', compute='_compute_total_conform_non_conform',
                                         store=True)
    total_non_conform_count = fields.Integer(string='Total Nombre Non Conforme',
                                             compute='_compute_total_conform_non_conform', store=True)

    # New state with "in_progress"
    state = fields.Selection([
        ('draft', 'Brouillon'),  # Draft
        ('in_progress', 'En cours'),  # In Progress
        ('closed', 'Clôturé'),  # Closed
        ('validated', 'Validée'),  # Validated
    ], string='Statut', default='draft')

    ppm = fields.Float(string="PPM", compute="_compute_ppm", store=True, digits=(16, 3))

    @api.depends('global_defect_rate')
    def _compute_ppm(self):
        for record in self:
            record.ppm = record.global_defect_rate * 10000  # 1% = 10,000 PPM


    @api.onchange('total_lines','total_lines_type1','total_lines_type2','total_lines_type3')
    def state_change(self):
        for record in self:
            print(f"Total Lines: {record.total_lines}, "
                  f"Qty Producing ntest: {record.product_qty}, "
                  f"Total lines type 1 : {record.total_lines_type1}, "
                  f"Total lines type 2 : {record.total_lines_type2}, "
                  f"Total lines type 3 : {record.total_lines_type3}, "
                  f"Current State: {record.state}")

            # Check if any types are selected and validate their quantities
            types_valid = True
            total_lines_selected = 0

            # Validate type_1
            if record.type_1:
                if record.total_lines_type1 != record.product_qty:
                    types_valid = False
                total_lines_selected += record.total_lines_type1

            # Validate type_2
            if record.type_2:
                if record.total_lines_type2 != record.product_qty:
                    types_valid = False
                total_lines_selected += record.total_lines_type2

            # Validate type_3
            if record.type_3:
                if record.total_lines_type3 != record.product_qty:
                    types_valid = False
                total_lines_selected += record.total_lines_type3

            # If no types are selected, revert to draft
            if total_lines_selected == 0:
                record.state = 'draft'
                print("State changed to draft - no types selected")
                continue

            # If any selected type's quantity doesn't match qty_producing_related,
            # set to in_progress
            if not types_valid:
                record.state = 'in_progress'
                print("State changed to in_progress - quantities don't match")
                continue

            # If all selected types have matching quantities, set to closed
            record.state = 'closed'
            print("State changed to closed - all quantities match")

    total_lines = fields.Integer(string='Total Lignes', compute='_compute_total_lines', readonly=True)
    # Add three fields for total lines of each type
    total_lines_type1 = fields.Integer(string='Total Lignes Type 1', compute='_compute_total_lines_type1', store=True)
    total_lines_type2 = fields.Integer(string='Total Lignes Type 2', compute='_compute_total_lines_type2', store=True)
    total_lines_type3 = fields.Integer(string='Total Lignes Type 3', compute='_compute_total_lines_type3', store=True)
    forced_closure = fields.Boolean(string='Cloture Forcée', default= False)
    @api.depends('type1_line_ids', 'type2_line_ids', 'type3_line_ids', 'type_1', 'type_2', 'type_3')
    def _compute_total_lines(self):
        for record in self:
            total_lines = 0

            # Check if type1 is enabled and add its lines to the total count
            if record.type_1:
                total_lines += len(record.type1_line_ids)

            # Check if type2 is enabled and add its lines to the total count
            if record.type_2:
                total_lines += len(record.type2_line_ids)

            # Check if type3 is enabled and add its lines to the total count
            if record.type_3:
                total_lines += len(record.type3_line_ids)

            record.total_lines = total_lines

    def action_cal_total_lines(self):
        for record in self:
            total_lines = 0

            # Check if type1 is enabled and add its lines to the total count
            if record.type_1:
                total_lines += len(record.type1_line_ids)

            # Check if type2 is enabled and add its lines to the total count
            if record.type_2:
                total_lines += len(record.type2_line_ids)

            # Check if type3 is enabled and add its lines to the total count
            if record.type_3:
                total_lines += len(record.type3_line_ids)

            record.total_lines = total_lines

    @api.depends('type1_line_ids')
    def _compute_total_lines_type1(self):
        for record in self:
            record.total_lines_type1 = len(record.type1_line_ids)

    @api.depends('type2_line_ids')
    def _compute_total_lines_type2(self):
        for record in self:
            record.total_lines_type2 = len(record.type2_line_ids)

    @api.depends('type3_line_ids')
    def _compute_total_lines_type3(self):
        for record in self:
            record.total_lines_type3 = len(record.type3_line_ids)

    # @api.onchange('total_lines_type1', 'total_lines_type2', 'total_lines_type3', 'qty_producing')
    # def validate_lines(self):
    #     for record in self:
    #         # Validate if all total lines match the quantity produced
    #         if (record.total_lines_type1 != record.qty_producing or
    #                 record.total_lines_type2 != record.qty_producing or
    #                 record.total_lines_type3 != record.qty_producing):
    #             raise exceptions.ValidationError(
    #                 "Les totaux de lignes ne correspondent pas à la quantité produite."
    #             )

    def action_validate(self):
        for record in self:
            # Ensure type-wise quantity matches `qty_producing`
            if record.forced_closure:
                record.state = 'validated'
            if record.type_1 and record.total_lines_type1 != record.product_qty and not record.forced_closure:
                raise exceptions.ValidationError(
                    "Erreur de validation : Le total des lignes de Type 1 doit correspondre à la quantité produite."
                )
            if record.type_2 and record.total_lines_type2 != record.product_qty and not record.forced_closure:
                raise exceptions.ValidationError(
                    "Erreur de validation : Le total des lignes de Type 2 doit correspondre à la quantité produite."
                )
            if record.type_3 and record.total_lines_type3 != record.product_qty and not record.forced_closure:
                raise exceptions.ValidationError(
                    "Erreur de validation : Le total des lignes de Type 3 doit correspondre à la quantité produite."
                )

            # If all checks pass, change state to 'done'
            record.state = 'validated'




    @api.onchange('type1_line_ids','type2_line_ids','type3_line_ids')
    def _compute_start_date(self):
        for record in self:
            if not record.start_date and record.total_lines:
                record.start_date= datetime.now()

    @api.onchange('type1_line_ids','type2_line_ids','type3_line_ids')
    def _compute_end_date(self):
        for record in self:
            if record.total_lines:
               record.end_date= datetime.now()

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.reference}"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('reference', '/') == '/':
            current_year = fields.Date.today().strftime('%y')
            sequence = self.env['ir.sequence'].next_by_code('control.quality') or '0001'
            of_name = self.env['mrp.production'].browse(vals.get('of_id')).name or 'OF'
            vals['reference'] = f"CQ - {current_year} - {sequence}"
        return super(QualityControl, self).create(vals)

    @api.depends('of_id')
    def _compute_of_id(self):
        if self.of_id:
            self.article_id = self.of_id.product_id.id
            self.client_reference = self.of_id.ref_product_client
            self.designation = self.of_id.description
            self.product_qty = self.of_id.product_qty
            self.original_product_qty = self.of_id.product_qty
            self.client_id = self.of_id.client_id
        else:
            # Reset values if of_id is cleared
            self.article_id = False
            self.client_reference = False
            self.designation = False
            self.qty_producing = False
            self.client_id = False

    @api.depends('type1_line_ids.result1')
    def _compute_conform_non_conform_type1(self):
        for record in self:
            conform_count = sum(1 for line in record.type1_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type1_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.type1_line_ids if line.result1 == 'client_default')
            record.type1_conform_count = conform_count
            record.type1_non_conform_count = non_conform_count
            record.type1_total_client_default = total_client_default

    @api.depends('type2_line_ids.result1')
    def _compute_conform_non_conform_type2(self):
        for record in self:
            conform_count = sum(1 for line in record.type2_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type2_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.type2_line_ids if line.result1 == 'client_default')
            record.type2_conform_count = conform_count
            record.type2_non_conform_count = non_conform_count
            record.type2_total_client_default = total_client_default

    @api.depends('type3_line_ids.result1')
    def _compute_conform_non_conform_type3(self):
        for record in self:
            conform_count = sum(1 for line in record.type3_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type3_line_ids if line.result1 == 'non_conform')
            total_client_default = sum(1 for line in record.type3_line_ids if line.result1 == 'client_default')
            record.type3_conform_count = conform_count
            record.type3_non_conform_count = non_conform_count
            record.type3_total_client_default = total_client_default

    @api.depends('type1_conform_count', 'type1_non_conform_count',
                 'type2_conform_count', 'type2_non_conform_count',
                 'type3_conform_count', 'type3_non_conform_count')
    def _compute_total_conform_non_conform(self):
        for record in self:
            record.total_conform_count = (
                    record.type1_conform_count +
                    record.type2_conform_count +
                    record.type3_conform_count
            )
            record.total_non_conform_count = (
                    record.type1_non_conform_count +
                    record.type2_non_conform_count +
                    record.type3_non_conform_count
            )

    @api.depends('type1_non_conform_count', 'total_lines_type1')
    def _compute_defect_rate_type1(self):
        for record in self:
            total_controlled = record.total_lines_type1
            if total_controlled > 0:
                record.type1_client_default_avg = (record.type1_non_conform_count / total_controlled) * 100
            else:
                record.type1_client_default_avg = 0.0

    @api.depends('type2_non_conform_count', 'total_lines_type2')  # Compute defect rate for Type 2
    def _compute_defect_rate_type2(self):
        for record in self:
            total_controlled = record.total_lines_type2
            if total_controlled > 0:
                record.type2_client_default_avg = (record.type2_non_conform_count / total_controlled) * 100
            else:
                record.type2_client_default_avg = 0.0

    @api.depends('type3_non_conform_count', 'total_lines_type3')  # Compute defect rate for Type 3
    def _compute_defect_rate_type3(self):
        for record in self:
            total_controlled = record.total_lines_type3
            if total_controlled > 0:
                record.type3_client_default_avg = (record.type3_non_conform_count / total_controlled) * 100
            else:
                record.type3_client_default_avg = 0.0

    barcode = fields.Char(string="Barcode", compute="_compute_barcode", store=True)

    @api.depends('reference')
    def _compute_barcode(self):
        for record in self:
            record.barcode = record.reference if record.reference else ''

    def action_force_closure(self):
        for record in self:
            record.state = 'closed'
            record.forced_closure = True

        # New fields to create
    original_product_qty = fields.Float(string='Original Quantity')
    product_qty_percentage = fields.Float(string='Quantity Percentage (%)', default=100.0)

    @api.onchange('manual_quantity', 'product_qty_percentage', 'original_product_qty')
    def _onchange_quantity_fields(self):
        for record in self:
            # When manual_quantity is toggled to True, store original value
            if record.manual_quantity and not record.original_product_qty:
                record.original_product_qty = record.product_qty

            # When manual_quantity is True, calculate product_qty based on percentage
            if record.manual_quantity and record.original_product_qty:
                record.product_qty = record.original_product_qty * (record.product_qty_percentage / 100.0)

            # When manual_quantity is toggled back to False, restore original value
            if not record.manual_quantity and record.original_product_qty:
                record.product_qty = record.original_product_qty
                record.product_qty_percentage = 100.0

    def write(self, vals):
        for record in self:
            # If updating the percentage and manual_quantity is enabled
            if 'product_qty_percentage' in vals and record.manual_quantity:
                percentage = vals.get('product_qty_percentage')
                if record.original_product_qty:
                    vals['product_qty'] = record.original_product_qty * (percentage / 100.0)

            # If enabling manual_quantity
            if 'manual_quantity' in vals and vals['manual_quantity'] and not record.original_product_qty:
                vals['original_product_qty'] = record.product_qty

            # If disabling manual_quantity
            if 'manual_quantity' in vals and not vals['manual_quantity'] and record.original_product_qty:
                vals['product_qty'] = record.original_product_qty
                vals['product_qty_percentage'] = 100.0

        return super(QualityControl, self).write(vals)
class QualityControlLine(models.Model):
    _name = 'control.quality.line'
    _description = 'Ligne de Contrôle Qualité'

    quality_id = fields.Many2one('control.quality', string='Contrôle Qualité', ondelete='cascade')
    serial_number = fields.Char(string='Numéro de Série', required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('passed', 'Passé'),
        ('failed', 'Échoué')
    ], string='État', required=True, default='pending')
