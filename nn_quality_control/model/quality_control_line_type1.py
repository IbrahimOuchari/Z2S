from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class QualityControlLineType1(models.Model):
    _name = 'control.quality.type1.line'
    _description = 'Ligne de Contrôle Qualité Type 1'

    quality_id = fields.Many2one('control.quality', string='Contrôle Qualité', ondelete='cascade')
    manu_of = fields.Many2one(
        'mrp.production',
        string='Ordre de Fabrication',
        compute='_compute_manu_of',
        store=True
    )

    @api.depends('quality_id')
    def _compute_manu_of(self):
        for record in self:
            record.manu_of = record.quality_id.of_id if record.quality_id else False

    @api.model
    def force_recompute_manu_of(self):
        for r in self.search([]):
            r._compute_manu_of()

    def action_force_manu_of(self):
        for rec in self:
            if rec.quality_id and rec.quality_id.of_id:
                rec.manu_of = rec.quality_id.of_id

    article_id = fields.Many2one('product.product', string='Article', compute='_compute_article',
                                 store=True)

    @api.depends('quality_id')
    def _compute_article(self):
        for record in self:
            record.article_id = record.quality_id.article_id if record.quality_id else False

    def action_force_article_id(self):
        for rec in self:
            if rec.quality_id and rec.quality_id.article_id:
                rec.article_id = rec.quality_id.article_id

    serial_number = fields.Char(string='Numéro de Série', required=True)
    other_info = fields.Text(string="Autre Info", default="RAS")

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

    # Created date field
    created_date = fields.Datetime(
        string='Date de Création',
        readonly=True,
        default=fields.Datetime.now
    )
    service_count = fields.Integer(
        string="Nombre de prestation",
        required=True,
        help="The number of services provided or handled.",
        default=1
    )

    # Controlleur field to fetch the current user
    controlleur_id = fields.Many2one('res.users', string='Contrôleur', readonly=True,
                                     default=lambda self: self.env.user)

    defect = fields.Many2one('defect.type', string='Défaut 1')
    defect1 = fields.Many2one('defect1.type', string='Défaut 1')
    defect2 = fields.Many2one('defect2.type', string='Défaut 2')
    reprise_id = fields.Many2one('reprise', string='Reprise')

    # Calcul des totaux
    total_conform = fields.Integer(string='Total Conforme', compute='_compute_totals')
    total_non_conform = fields.Integer(string='Total Non Conforme', compute='_compute_totals')
    total_client_default = fields.Integer(string='Total Client Défault', compute='_compute_total_client_default')

    @api.depends('result1', 'result2')
    def _compute_total_client_default(self):
        for record in self:
            total_client_default = self.search_count([
                ('result1', '=', 'client_default'),
                ('result2', '=', 'client_default')
            ])
            record.total_client_default = total_client_default

    @api.depends('result1', 'result2')
    def _compute_totals(self):
        for record in self:
            total_conform = self.search_count([
                ('result1', '=', 'conform'),
                ('result2', '=', 'conform'),
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

        return super(QualityControlLineType1, self).create(vals)

    def write(self, vals):
        # If 'timestamp' is being updated, don't overwrite it with the default value
        if 'timestamp' not in vals:
            vals['timestamp'] = datetime.now()  # Keep the current value of 'timestamp'

        return super(QualityControlLineType1, self).write(vals)
