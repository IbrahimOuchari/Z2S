from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


class QualityControlLineType2(models.Model):
    _name = 'control.quality.type2.line'
    _description = 'Ligne de Contrôle Qualité Type 2'

    serial_number = fields.Char(string='Numéro de Série', required=True)
    quality_id = fields.Many2one('control.quality', string='Contrôle Qualité', ondelete='cascade')
    manu_of = fields.Many2one('mrp.production', string='Ordre de Fabrication', ondelete='cascade')
    other_info = fields.Text(string="Autre Info" ,default="RAS")
    service_count = fields.Integer(
        string="Nombre de prestation",
        required=True,
        help="The number of services provided or handled.",
        default=1
    )

    @api.constrains('serial_number')
    def check_serial_number_unique(self):
        for record in self:
            if record.serial_number and record.quality_id:
                # Get all lines for the current quality_id in their correct order
                all_lines = self.search([
                    ('quality_id', '=', record.quality_id.id)
                ], order='id')

                # Create a list of line numbers with their serial numbers
                line_mapping = []
                for idx, line in enumerate(all_lines, 1):
                    line_mapping.append({
                        'line_number': idx,
                        'serial_number': line.serial_number,
                        'id': line.id
                    })

                # Find duplicates
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
                    raise ValidationError(
                        f"Le numéro de série '{record.serial_number}' à la ligne {current_line_number} "
                        f"est déjà utilisé à la ligne {duplicate_line_number} "
                        f"dans ce contrôle qualité"
                    )
    operator_id = fields.Many2one('hr.employee', string='Opérateur')

    # Conformité
    result1 = fields.Selection([
        ('conform', 'Conforme'),
        ('non_conform', 'Non Conforme'),
        ('client_default', 'Défaut client ')
    ], string='Résultat 1', default="conform", required=True)

    result2 = fields.Selection([
        ('conform', 'Conforme'),
        ('non_conform', 'Non Conforme'),
        ('client_default', 'Défaut client ')
    ], string='Résultat 2')

    # Change to Many2one
    defect1 = fields.Many2one('defect1.type', string='Défaut 1')
    defect2 = fields.Many2one('defect2.type', string='Défaut 2')
    reprise_id = fields.Many2one('reprise', string='Reprise')

    # Calcul des totaux
    total_conform = fields.Integer(string='Total Conforme', compute='_compute_totals')
    total_non_conform = fields.Integer(string='Total Non Conforme', compute='_compute_totals')
    created_date = fields.Datetime(string='Date de création', default=fields.Datetime.now, readonly=True)
    controlleur_id = fields.Many2one('res.users', string='Contrôleur', readonly=True,
                                     default=lambda self: self.env.user)

    @api.depends('result1', 'result2')
    def _compute_totals(self):
        for record in self:
            total_conform = self.search_count([
                ('result1', '=', 'conform'),
                ('result2', '=', 'conform')
            ])
            total_non_conform = self.search_count([
                '|',
                ('result1', '=', 'non_conform'),
                ('result2', '=', 'non_conform')
            ])
            record.total_conform = total_conform
            record.total_non_conform = total_non_conform



    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        # Set 'timestamp' only if it's not in vals (i.e., the field is empty)
        if 'timestamp' not in vals or not vals['timestamp']:
            vals['timestamp'] = datetime.now()  # Use current timestamp if not set

        return super(QualityControlLineType2, self).create(vals)

    def write(self, vals):
        # If 'timestamp' is being updated, don't overwrite it with the default value
        if 'timestamp' not in vals:
            vals['timestamp'] = datetime.now()  # Keep the current value of 'timestamp'

        return super(QualityControlLineType2, self).write(vals)