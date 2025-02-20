from odoo import models, fields, api


class QualityControlLineType2(models.Model):
    _name = 'control.quality.type2.line'
    _description = 'Ligne de Contrôle Qualité Type 2'

    quality_id = fields.Many2one('control.quality', string='Contrôle Qualité', ondelete='cascade')
    serial_number = fields.Char(string='Numéro de Série', required=True, unique=True)
    # Add SQL constraint for uniqueness
    _sql_constraints = [
        ('unique_serial_number', 'unique(serial_number)', "Le numéro de série doit être unique.")
    ]
    # Fetching operator from HR Employee
    operator_id = fields.Many2one('hr.employee', string='Opérateur')

    # Conformité
    result1 = fields.Selection([
        ('conform', 'Conforme'),
        ('non_conform', 'Non Conforme')
    ], string='Résultat 1', default="conform", required=True)

    result2 = fields.Selection([
        ('conform', 'Conforme'),
        ('non_conform', 'Non Conforme')
    ], string='Résultat 2')

    # Change to Many2one
    defect_type_id = fields.Many2one('defect.type', string='Type de Défaut')
    reprise_id = fields.Many2one('reprise', string='Reprise')

    # Calcul des totaux
    total_conform = fields.Integer(string='Total Conforme', compute='_compute_totals')
    total_non_conform = fields.Integer(string='Total Non Conforme', compute='_compute_totals')

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

    @api.onchange('result1', 'result2')
    def _onchange_result(self):
        """Display Defect Type and Reprise only if either result1 or result2 is Non-Conforme."""
        if self.result1 == 'non_conform' or self.result2 == 'non_conform':
            self.defect_type_id = False
            self.reprise_id = False
        else:
            self.defect_type_id = False
            self.reprise_id = False
