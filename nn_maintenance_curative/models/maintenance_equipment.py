import logging
from datetime import datetime, timedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    period_count = fields.Selection(
        selection=[
            ('1', 'Mensuelle'),
            ('2', 'Trimestrielle'),
            ('3', 'Semestrielle'),
            ('4', 'Annuelle'),
        ],
        string="Fréquence",
        default='1',
    )
    period_1_frequency = fields.Integer("Période 1 (en jours)")
    period_2_frequency = fields.Integer("Période 2 (en jours)")
    period_3_frequency = fields.Integer("Période 3 (en jours)")
    period_4_frequency = fields.Integer("Période 4 (en jours)")
    state = fields.Integer("Période 4 (en jours)")

    effective_date = fields.Date("Date effective")

    start_maintenance_date = fields.Date(
        string="Date début maintenance",
        compute="_compute_start_maintenance_date",
        store=True,
        readonly=False,
    )

    next_maintenance_date = fields.Date(
        string="Prochaine maintenance",
        compute="_compute_next_maintenance_date",
        store=True
    )

    intervention_ligne_ids_1 = fields.One2many('maintenance.intervention.line1', 'equipment_id',
                                               string="Intervention fréquence 1", domain=[('frequency', '=', '1')])
    intervention_ligne_ids_2 = fields.One2many('maintenance.intervention.line2', 'equipment_id',
                                               string="Intervention fréquence 2", domain=[('frequency', '=', '2')])
    intervention_ligne_ids_3 = fields.One2many('maintenance.intervention.line3', 'equipment_id',
                                               string="Intervention fréquence 3", domain=[('frequency', '=', '3')])
    intervention_ligne_ids_4 = fields.One2many('maintenance.intervention.line4', 'equipment_id',
                                               string="Intervention fréquence 4", domain=[('frequency', '=', '4')])

    reference_intervention = fields.Char(string="Référence", compute='_compute_reference_intervention', readonly=False)

    @api.onchange('period_count')
    def _compute_reference_intervention(self):
        for rec in self:
            rec.reference_intervention = rec.reference_interne

    poste = fields.Char(string="Poste")
    date_heure_debut_1 = fields.Datetime(string="Date début fréquence 1", compute="_compute_date_debut", store=True)
    date_heure_debut_2 = fields.Datetime(string="Date début fréquence 2", compute="_compute_date_debut", store=True)
    date_heure_debut_3 = fields.Datetime(string="Date début fréquence 3", compute="_compute_date_debut", store=True)
    date_heure_debut_4 = fields.Datetime(string="Date début fréquence 4", compute="_compute_date_debut", store=True)
    date_heure_fin = fields.Datetime(string="Date et heure fin")

    @api.depends('period_1_frequency', 'period_2_frequency', 'period_3_frequency', 'period_4_frequency')
    def _compute_date_debut(self):
        for rec in self:
            today = datetime.today()
            rec.date_heure_debut_1 = today + timedelta(days=rec.period_1_frequency) if rec.period_1_frequency else False
            rec.date_heure_debut_2 = today + timedelta(days=rec.period_2_frequency) if rec.period_2_frequency else False
            rec.date_heure_debut_3 = today + timedelta(days=rec.period_3_frequency) if rec.period_3_frequency else False
            rec.date_heure_debut_4 = today + timedelta(days=rec.period_4_frequency) if rec.period_4_frequency else False

    @api.onchange('period_count')
    def _onchange_period_count(self):
        """Update UI when period_count changes"""
        _logger.info("Entering _onchange_period_count with period_count: %s", self.period_count)
        self._create_intervention_lines()

    def _create_intervention_lines(self):
        """Create intervention lines based on period_count"""
        _logger.info("Creating intervention lines with period_count: %s", self.period_count)

        if not self.period_count:
            _logger.warning("period_count is not set, exiting function.")
            return

        freq_number = int(self.period_count)
        _logger.info("Converted period_count to integer: %d", freq_number)

        # Fetch all operations
        operations = self.env['maintenance.operation.list'].search([('equipment_id', '=', self.id)])
        _logger.info("Fetched %d operations ", len(operations))

        # Clear existing lines before populating new ones
        self.intervention_ligne_ids_1 = [(5, 0, 0)]
        self.intervention_ligne_ids_2 = [(5, 0, 0)]
        self.intervention_ligne_ids_3 = [(5, 0, 0)]
        self.intervention_ligne_ids_4 = [(5, 0, 0)]

        # Initialize lists to store operation records for each frequency
        line_1 = []
        line_2 = []
        line_3 = []
        line_4 = []

        # Iterate through operations and collect names based on frequency
        for op in operations:
            if op.equipment_id.id == self.id:
                if op.is_mensuelle:
                    line_1.append((0, 0, {
                        'frequency': '1',
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,  # Explicitly set the parent equipment_id
                    }))
                _logger.info("Added operation_id %s to line_1", op.id)
                if op.is_trimestrielle:
                    line_2.append((0, 0, {
                        'frequency': '2',
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,  # Explicitly set the parent equipment_id
                    }))
                _logger.info("Added operation_id %s to line_2", op.id)
                if op.is_semestrielle:
                    line_3.append((0, 0, {
                        'frequency': '3',
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,  # Explicitly set the parent equipment_id
                    }))
                _logger.info("Added operation_id %s to line_3", op.id)
                if op.is_annuelle:
                    line_4.append((0, 0, {
                        'frequency': '4',
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,  # Explicitly set the parent equipment_id
                    }))
                _logger.info("Added operation_id %s to line_4", op.id)

        # Assign the collected lines to the respective intervention fields
        self.intervention_ligne_ids_1 = line_1
        self.intervention_ligne_ids_2 = line_2
        self.intervention_ligne_ids_3 = line_3
        self.intervention_ligne_ids_4 = line_4

        # Log the content of each intervention line
        _logger.info("Content of intervention_ligne_ids_1 (frequency '1'): %s", line_1)
        _logger.info("Content of intervention_ligne_ids_2 (frequency '2'): %s", line_2)
        _logger.info("Content of intervention_ligne_ids_3 (frequency '3'): %s", line_3)
        _logger.info("Content of intervention_ligne_ids_4 (frequency '4'): %s", line_4)

    @api.model
    def create(self, vals):
        """Override create to ensure intervention lines are created on record creation"""
        record = super(MaintenanceEquipment, self).create(vals)
        if vals.get('period_count'):
            record._create_intervention_lines()
        return record

    def write(self, vals):
        """Override write to ensure intervention lines are updated when period_count changes"""
        result = super(MaintenanceEquipment, self).write(vals)
        if 'period_count' in vals:
            for record in self:
                record._create_intervention_lines()
        return result

    @api.depends('effective_date', 'period_1_frequency', 'period_2_frequency', 'period_3_frequency',
                 'period_4_frequency')
    def _compute_start_maintenance_date(self):
        for record in self:
            if record.effective_date:
                freqs = [
                    record.period_1_frequency,
                    record.period_2_frequency,
                    record.period_3_frequency,
                    record.period_4_frequency
                ]
                freqs = [f for f in freqs if f]
                if freqs:
                    min_freq = min(freqs)
                    record.start_maintenance_date = record.effective_date + timedelta(days=min_freq)
                else:
                    record.start_maintenance_date = False
            else:
                record.start_maintenance_date = False

    @api.depends('date_heure_debut_1', 'date_heure_debut_2', 'date_heure_debut_3', 'date_heure_debut_4')
    def _compute_next_maintenance_date(self):
        for rec in self:
            all_dates = list(filter(None, [
                rec.date_heure_debut_1,
                rec.date_heure_debut_2,
                rec.date_heure_debut_3,
                rec.date_heure_debut_4,
            ]))
            rec.next_maintenance_date = min(all_dates).date() if all_dates else False
