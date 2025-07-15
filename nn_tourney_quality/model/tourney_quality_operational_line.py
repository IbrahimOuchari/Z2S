from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TourneyQualityOperationalLine(models.Model):
    _name = 'tourney.quality.operational.line'
    _description = 'Tourney Quality Operational Control Line'

    quality_id = fields.Many2one('tourney.quality', string='Tourney Quality', ondelete='cascade')
    article_id = fields.Many2one(related='quality_id.article_id', string='Article', store=True)
    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        compute='_compute_manufacturing_order_id',
        store=True
    )
    quality_list_id = fields.Many2one(
        'tourney.quality.operational.list',
        string='Operational List',
        ondelete='cascade'
    )

    @api.depends('quality_id')
    def _compute_manufacturing_order_id(self):
        for record in self:
            record.manufacturing_order_id = record.quality_id.of_id if record.quality_id else False

    serial_number = fields.Char(string='Serial Number', required=True)

    # New fields
    operator_id = fields.Many2one('hr.employee', string='Operator')
    controlleur_id = fields.Many2one('res.users', string='Controller', readonly=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    # Replaced 'result' with 'result1' and added 'result2'
    result1 = fields.Selection([
        ('conform', 'Conform'),
        ('non_conform', 'Non-Conform'),
        ('client_default', 'Client Defect'),
    ], string='Result 1', default='conform', required=True)

    result2 = fields.Selection([
        ('conform', 'Conform'),
        ('non_conform', 'Non-Conform'),
        ('client_default', 'Client Defect'),
    ], string='Result 2')

    other_info = fields.Text(string="Other Info", default="RAS")

    # Many2one fields linking to the specific defect/reprise models (from previous step)
    defect1_type_id = fields.Many2one(
        'tourney.quality.operational.line.defect1',
        string='Defect Type 1'
    )
    defect2_type_id = fields.Many2one(
        'tourney.quality.operational.line.defect2',
        string='Defect Type 2'
    )
    reprise_type_id = fields.Many2one(
        'tourney.quality.operational.line.reprise',
        string='Rework Type'
    )

    @api.constrains('serial_number')
    def check_serial_number_unique(self):
        for record in self:
            if record.serial_number and record.quality_id:
                all_lines = self.search([
                    ('quality_id', '=', record.quality_id.id)
                ], order='id')

                line_mapping = []
                for idx, line in enumerate(all_lines, 1):
                    line_mapping.append({
                        'line_number': idx,
                        'serial_number': line.serial_number,
                        'id': line.id
                    })

                current_line_number = next(
                    (item['line_number'] for item in line_mapping if item['id'] == record.id),
                    None
                )

                duplicate_line_number = next(
                    (item['line_number'] for item in line_mapping
                     if item['serial_number'] == record.serial_number
                     and item['id'] != record.id),
                    None
                )

                if duplicate_line_number:
                    raise ValidationError(_(
                        f"The serial number '{record.serial_number}' in line {current_line_number} "
                        f"is already used in line {duplicate_line_number} "
                        f"for this Tourney Quality record."
                    ))

    @api.onchange('result1')  # Changed from 'result' to 'result1'
    def _onchange_result1(self):
        """ Clear defect/reprise fields if result1 is 'conform' """
        if self.result1 == 'conform':
            self.defect1_type_id = False
            self.defect2_type_id = False
            self.reprise_type_id = False

    @api.model
    def create(self, vals):
        if 'controlleur_id' not in vals or not vals['controlleur_id']:
            vals['controlleur_id'] = self.env.user.id
        if 'timestamp' not in vals or not vals['timestamp']:
            vals['timestamp'] = fields.Datetime.now()

        return super(TourneyQualityOperationalLine, self).create(vals)

    def write(self, vals):
        if 'timestamp' not in vals:
            vals['timestamp'] = fields.Datetime.now()
        return super(TourneyQualityOperationalLine, self).write(vals)
