from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TourneyQualityProductLine(models.Model):
    _name = 'tourney.quality.product.line'
    _description = 'Tourney Quality Product Control Line'

    quality_id = fields.Many2one('tourney.quality', string='Tourney Quality', ondelete='cascade')
    article_id = fields.Many2one(related='quality_id.article_id', string='Article', store=True)
    manufacturing_order_id = fields.Many2one(
        'mrp.production',
        string='Manufacturing Order',
        compute='_compute_manufacturing_order_id',
        store=True
    )

    @api.depends('quality_id')
    def _compute_manufacturing_order_id(self):
        for record in self:
            record.manufacturing_order_id = record.quality_id.of_id if record.quality_id else False

    serial_number = fields.Char(string='Serial Number', required=True)

    # New fields (same as other lines, but WITHOUT defect/reprise specific fields)
    operator_id = fields.Many2one('hr.employee', string='Operator')
    controlleur_id = fields.Many2one('res.users', string='Controller', readonly=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    service_count = fields.Integer(
        string="Nombre de prestation",
        required=True,
        help="The number of services provided or handled.",
        default=1
    )

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
    defect1 = fields.Many2one('defect1.type', string='Défaut 1')
    defect2 = fields.Many2one('defect2.type', string='Défaut 2')
    reprise_id = fields.Many2one('reprise', string='Reprise')

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

    @api.model
    def create(self, vals):
        if 'controlleur_id' not in vals or not vals['controlleur_id']:
            vals['controlleur_id'] = self.env.user.id
        if 'timestamp' not in vals or not vals['timestamp']:
            vals['timestamp'] = fields.Datetime.now()

        return super(TourneyQualityProductLine, self).create(vals)

    def write(self, vals):
        if 'timestamp' not in vals:
            vals['timestamp'] = fields.Datetime.now()
        return super(TourneyQualityProductLine, self).write(vals)
