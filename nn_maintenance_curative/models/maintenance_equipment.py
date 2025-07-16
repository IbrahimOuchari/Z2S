import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    calendar_event_ids = fields.One2many(
        'maintenance.calendar.event',
        'equipment_id',
        string="Événements de maintenance"
    )

    period_1_frequency = fields.Integer("Période 1 (en jours)")
    period_2_frequency = fields.Integer("Période 2 (en jours)")
    period_3_frequency = fields.Integer("Période 3 (en jours)")
    period_4_frequency = fields.Integer("Période 4 (en jours)")

    state = fields.Integer("Période 4 (en jours)")

    period_1_warning = fields.Html(string="Alerte Période 1", compute="_compute_warnings")
    period_2_warning = fields.Html(string="Alerte Période 2", compute="_compute_warnings")
    period_3_warning = fields.Html(string="Alerte Période 3", compute="_compute_warnings")
    period_4_warning = fields.Html(string="Alerte Période 4", compute="_compute_warnings")

    @api.depends('period_1_frequency', 'period_2_frequency', 'period_3_frequency', 'period_4_frequency')
    def _compute_warnings(self):
        for rec in self:
            if rec.period_1_frequency:
                if rec.period_1_frequency < 1:
                    rec.period_1_warning = "<div class='note-warning'>⚠️ La période mensuelle doit être au moins 1 jour !</div>"
                elif rec.period_1_frequency > 31:
                    rec.period_1_warning = f"<div class='note-warning'>⚠️ Période mensuelle trop longue : {rec.period_1_frequency} jours (max 31) !</div>"
                else:
                    rec.period_1_warning = False
            else:
                rec.period_1_warning = False

            if rec.period_2_frequency:
                if rec.period_2_frequency < 1:
                    rec.period_2_warning = "<div class='note-warning'>⚠️ La période trimestrielle doit être au moins 1 jour !</div>"
                elif rec.period_2_frequency > 93:
                    rec.period_2_warning = f"<div class='note-warning'>⚠️ Période trimestrielle trop longue : {rec.period_2_frequency} jours (max 93) !</div>"
                else:
                    rec.period_2_warning = False
            else:
                rec.period_2_warning = False

            if rec.period_3_frequency:
                if rec.period_3_frequency < 1:
                    rec.period_3_warning = "<div class='note-warning'>⚠️ La période semestrielle doit être au moins 1 jour !</div>"
                elif rec.period_3_frequency > 186:
                    rec.period_3_warning = f"<div class='note-warning'>⚠️ Période semestrielle trop longue : {rec.period_3_frequency} jours (max 186) !</div>"
                else:
                    rec.period_3_warning = False
            else:
                rec.period_3_warning = False

            if rec.period_4_frequency:
                if rec.period_4_frequency < 1:
                    rec.period_4_warning = "<div class='note-warning'>⚠️ La période annuelle doit être au moins 1 jour !</div>"
                elif rec.period_4_frequency > 366:
                    rec.period_4_warning = f"<div class='note-warning'>⚠️ Période annuelle trop longue : {rec.period_4_frequency} jours (max 366) !</div>"
                else:
                    rec.period_4_warning = False
            else:
                rec.period_4_warning = False

    @api.constrains('period_1_frequency', 'period_2_frequency', 'period_3_frequency', 'period_4_frequency')
    def _check_period_frequencies(self):
        for rec in self:
            errors = []
            if rec.period_1_frequency and not (1 <= rec.period_1_frequency <= 31):
                errors.append("La période mensuelle doit être comprise entre 1 et 31 jours.")
            if rec.period_2_frequency and not (32 <= rec.period_2_frequency <= 93):
                errors.append("La période trimestrielle doit être comprise entre 32 et 93 jours.")
            if rec.period_3_frequency and not (94 <= rec.period_3_frequency <= 186):
                errors.append("La période semestrielle doit être comprise entre 94 et 186 jours.")
            if rec.period_4_frequency and not (1 <= rec.period_4_frequency <= 366):
                errors.append("La période annuelle doit être comprise entre 187 et 366 jours.")
            if errors:
                raise ValidationError('\n'.join(errors))

    effective_date = fields.Date("Date effective")
    start_maintenance_date = fields.Date(
        string="Date début maintenance",
        store=True,
        readonly=False,
    )

    next_maintenance_mensuelle = fields.Date(
        string="Prochaine maintenance mensuelle",
        compute="_compute_next_maintenance_mensuelle",
        store=True
    )
    next_maintenance_trimestrielle = fields.Date(
        string="Prochaine maintenance trimestrielle",
        compute="_compute_next_maintenance_trimestrielle",
        store=True
    )
    next_maintenance_semestrielle = fields.Date(
        string="Prochaine maintenance semestrielle",
        compute="_compute_next_maintenance_semestrielle",
        store=True
    )
    next_maintenance_annuelle = fields.Date(
        string="Prochaine maintenance annuelle",
        compute="_compute_next_maintenance_annuelle",
        store=True
    )

    sync_calendar_flag = fields.Boolean(compute="_compute_sync_calendar_all", default=False)

    @api.onchange(
        'period_1_frequency',
        'period_2_frequency',
        'period_3_frequency',
        'period_4_frequency',
        'start_maintenance_date',
        'is_mensuelle',
        'is_trimestrielle',
        'is_semestrielle',
        'is_annuelle',
    )
    def _compute_sync_calendar_all(self):
        for rec in self:
            if not rec.start_maintenance_date:
                rec.sync_calendar_flag = False  # ✅ Now we assign a value even if skipped
                continue

            start = rec.start_maintenance_date

            if rec.period_1_frequency and rec.is_mensuelle:
                date_1 = start + timedelta(days=rec.period_1_frequency)
                rec._sync_calendar_event('1', rec.period_1_frequency, date_1)
            if rec.period_2_frequency and rec.is_trimestrielle:
                date_2 = start + timedelta(days=rec.period_2_frequency)
                rec._sync_calendar_event('2', rec.period_2_frequency, date_2)
            if rec.period_3_frequency and rec.is_semestrielle:
                date_3 = start + timedelta(days=rec.period_3_frequency)
                rec._sync_calendar_event('3', rec.period_3_frequency, date_3)
            if rec.period_4_frequency and rec.is_annuelle:
                date_4 = start + timedelta(days=rec.period_4_frequency)
                rec._sync_calendar_event('4', rec.period_4_frequency, date_4)

            rec.sync_calendar_flag = True

    cleanup_flag = fields.Boolean(compute="_compute_cleanup_calendar_events")

    @api.onchange(
        'period_1_frequency',
        'period_2_frequency',
        'period_3_frequency',
        'period_4_frequency',
        'is_mensuelle',
        'is_trimestrielle',
        'is_semestrielle',
        'is_annuelle',
    )
    def _compute_cleanup_calendar_events(self):
        for rec in self:
            try:
                periods_to_delete = []
                # Check period 1
                if not rec.is_mensuelle or not rec.period_1_frequency:
                    periods_to_delete.append('1')
                # Check period 2
                if not rec.is_trimestrielle or not rec.period_2_frequency:
                    periods_to_delete.append('2')
                # Check period 3
                if not rec.is_semestrielle or not rec.period_3_frequency:
                    periods_to_delete.append('3')
                # Check period 4
                if not rec.is_annuelle or not rec.period_4_frequency:
                    periods_to_delete.append('4')

                # If all are to be deleted → delete all
                if len(periods_to_delete) == 4:
                    rec._delete_calendar_event_by_period()
                else:
                    for period in periods_to_delete:
                        rec._delete_calendar_event_by_period(period)
                rec.cleanup_flag = True
            except Exception as e:
                _logger.error("Error while cleaning calendar events for equipment %s: %s", rec.name or rec.id, e)
                rec.cleanup_flag = False

    def _delete_calendar_event_by_period(self, period_key=None):
        """Delete calendar events for the current equipment and (optionally) a specific period."""
        self.ensure_one()
        domain = [('equipment_id', '=', self.id)]
        if period_key:
            domain.append(('period_count', '=', period_key))
        events = self.env['maintenance.calendar.event'].search(domain)
        if events:
            events.unlink()

    def _sync_calendar_event(self, period_key, frequency_days, start_date):
        """Always remove any existing event (and its lines), then recreate if needed."""
        for record in self:
            if not record.id:
                continue
            # 1) Unlink any existing event (and cascade-delete its lines)
            existing = self.env['maintenance.calendar.event'].search([
                ('equipment_id', '=', record.id),
                ('period_count', '=', period_key),
            ], limit=1)
            if existing:
                existing.unlink()
            # 2) If no frequency → done (we’ve already cleaned up)
            if not frequency_days:
                continue
            # 3) Need a start date to build a new series
            if not start_date:
                continue
            # 4) Create fresh event + lines
            vals = {
                'name': record.name or 'Maintenance',
                'period_count': period_key,
                'equipment_id': record.id,
                'frequency_days': frequency_days,
                'start_maintenance_date': start_date,
            }
            new_event = self.env['maintenance.calendar.event'].create(vals)
            new_event.generate_lines()

    @api.onchange('start_maintenance_date', 'period_1_frequency', 'is_mensuelle')
    def _compute_next_maintenance_mensuelle(self):
        for record in self:
            freq = record.period_1_frequency
            start = record.start_maintenance_date or fields.Date.today()
            if freq and record.is_mensuelle:
                start_date = start + timedelta(days=freq)
                record.next_maintenance_mensuelle = start_date
                record._sync_calendar_event('1', freq, start_date)
            else:
                record.next_maintenance_mensuelle = False

    @api.onchange('start_maintenance_date', 'period_2_frequency', 'is_trimestrielle')
    def _compute_next_maintenance_trimestrielle(self):
        for record in self:
            freq = record.period_2_frequency
            start = record.start_maintenance_date or fields.Date.today()
            if freq and record.is_trimestrielle:
                start_date = start + timedelta(days=freq)
                record.next_maintenance_trimestrielle = start_date
                record._sync_calendar_event('2', freq, start_date)
            else:
                record.next_maintenance_trimestrielle = False

    @api.onchange('start_maintenance_date', 'period_3_frequency', 'is_semestrielle')
    def _compute_next_maintenance_semestrielle(self):
        for record in self:
            freq = record.period_3_frequency
            start = record.start_maintenance_date or fields.Date.today()
            if freq and record.is_semestrielle:
                start_date = start + timedelta(days=freq)
                record.next_maintenance_semestrielle = start_date
                record._sync_calendar_event('3', freq, start_date)
            else:
                record.next_maintenance_semestrielle = False

    @api.onchange('start_maintenance_date', 'period_4_frequency', 'is_annuelle')
    def _compute_next_maintenance_annuelle(self):
        for record in self:
            freq = record.period_4_frequency
            start = record.start_maintenance_date or fields.Date.today()
            if freq and record.is_annuelle:
                start_date = start + timedelta(days=freq)
                record.next_maintenance_annuelle = start_date
                record._sync_calendar_event('4', freq, start_date)
            else:
                record.next_maintenance_annuelle = False

    intervention_ligne_ids_1 = fields.One2many(
        'maintenance.intervention.line1', 'equipment_id',
        string="Intervention fréquence 1",
    )

    intervention_ligne_ids_2 = fields.One2many(
        'maintenance.intervention.line2', 'equipment_id',
        string="Intervention fréquence 2",
    )

    intervention_ligne_ids_3 = fields.One2many(
        'maintenance.intervention.line3', 'equipment_id',
        string="Intervention fréquence 3",
    )

    intervention_ligne_ids_4 = fields.One2many(
        'maintenance.intervention.line4', 'equipment_id',
        string="Intervention fréquence 4",

    )

    reference_intervention = fields.Char(string="Référence", compute='_compute_reference_intervention', readonly=False)

    @api.onchange('is_mensuelle', 'is_trimestrielle', 'is_semestrielle', 'is_annuelle')
    def _compute_reference_intervention(self):
        for rec in self:
            rec.reference_intervention = rec.reference_interne

    poste = fields.Char(string="Poste")

    date_heure_debut_1 = fields.Datetime(string="Date début maintenance Mensuelle", compute="_compute_date_debut",
                                         store=True)
    date_heure_debut_2 = fields.Datetime(string="Date début maintenance Trimestrielle", compute="_compute_date_debut",
                                         store=True)
    date_heure_debut_3 = fields.Datetime(string="Date début maintenance Semestrielle", compute="_compute_date_debut",
                                         store=True)
    date_heure_debut_4 = fields.Datetime(string="Date début maintenance Annuelle", compute="_compute_date_debut",
                                         store=True)

    date_heure_fin_1 = fields.Datetime(string="Date et heure fin")
    date_heure_fin_2 = fields.Datetime(string="Date et heure fin")
    date_heure_fin_3 = fields.Datetime(string="Date et heure fin")
    date_heure_fin_4 = fields.Datetime(string="Date et heure fin")

    @api.onchange('period_1_frequency', 'period_2_frequency', 'period_3_frequency', 'period_4_frequency',
                  'start_maintenance_date')
    def _compute_date_debut(self):
        for rec in self:
            today = datetime.today()
            rec.date_heure_debut_1 = rec.start_maintenance_date + timedelta(
                days=rec.period_1_frequency) if rec.period_1_frequency and rec.is_mensuelle else False
            rec.date_heure_debut_2 = rec.start_maintenance_date + timedelta(
                days=rec.period_2_frequency) if rec.period_2_frequency and rec.is_trimestrielle else False
            rec.date_heure_debut_3 = rec.start_maintenance_date + timedelta(
                days=rec.period_3_frequency) if rec.period_3_frequency and rec.is_semestrielle else False
            rec.date_heure_debut_4 = rec.start_maintenance_date + timedelta(
                days=rec.period_4_frequency) if rec.period_4_frequency and rec.is_annuelle else False

    period_changed = fields.Integer(compute='compute_period_changes')

    @api.depends('is_mensuelle', 'is_trimestrielle', 'is_semestrielle', 'is_annuelle')
    def compute_period_changes(self):
        """Update UI when period checkboxes change"""
        _logger.info("Entering _onchange_period_count")

        self._create_intervention_lines()
        self.period_changed += 1

    def _create_intervention_lines(self):
        """Create intervention lines based on period checkboxes"""
        self.ensure_one()  # ensure single record for safety

        _logger.info("Creating intervention lines for equipment ID %s", self.id)

        operations = self.env['maintenance.operation.list'].search([('equipment_id', '=', self.id)])
        _logger.info("Fetched %d operations", len(operations))

        # Clear existing lines before populating new ones
        self.intervention_ligne_ids_1 = [(5, 0, 0)]
        self.intervention_ligne_ids_2 = [(5, 0, 0)]
        self.intervention_ligne_ids_3 = [(5, 0, 0)]
        self.intervention_ligne_ids_4 = [(5, 0, 0)]

        line_1 = []
        line_2 = []
        line_3 = []
        line_4 = []

        for op in operations:
            if op.equipment_id.id == self.id:
                if op.is_mensuelle and getattr(self, 'is_mensuelle', False):
                    line_1.append((0, 0, {
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,
                        'is_mensuelle': True,
                    }))
                    _logger.info("Added operation_id %s to line_1 (Mensuelle)", op.id)
                if op.is_trimestrielle and getattr(self, 'is_trimestrielle', False):
                    line_2.append((0, 0, {
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,
                        'is_trimestrielle': True,
                    }))
                    _logger.info("Added operation_id %s to line_2 (Trimestrielle)", op.id)
                if op.is_semestrielle and getattr(self, 'is_semestrielle', False):
                    line_3.append((0, 0, {
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,
                        'is_semestrielle': True,
                    }))
                    _logger.info("Added operation_id %s to line_3 (Semestrielle)", op.id)
                if op.is_annuelle and getattr(self, 'is_annuelle', False):
                    line_4.append((0, 0, {
                        'operation_name': op.name,
                        'operation_id': op.id,
                        'equipment_id': self.id,
                        'is_annuelle': True,
                    }))
                    _logger.info("Added operation_id %s to line_4 (Annuelle)", op.id)

        # Assign the collected lines to the respective fields
        self.intervention_ligne_ids_1 = line_1
        self.intervention_ligne_ids_2 = line_2
        self.intervention_ligne_ids_3 = line_3
        self.intervention_ligne_ids_4 = line_4

        # Log the content of each intervention line for debugging
        _logger.info("intervention_ligne_ids_1: %s", line_1)
        _logger.info("intervention_ligne_ids_2: %s", line_2)
        _logger.info("intervention_ligne_ids_3: %s", line_3)
        _logger.info("intervention_ligne_ids_4: %s", line_4)

    @api.model
    def create(self, vals):
        """Override create to ensure intervention lines are created on record creation"""
        record = super(MaintenanceEquipment, self).create(vals)
        record._create_intervention_lines()
        return record

    def write(self, vals):
        """Override write to ensure intervention lines are updated when period checkboxes change"""
        result = super(MaintenanceEquipment, self).write(vals)
        if any(field in vals for field in ['is_mensuelle', 'is_trimestrielle', 'is_semestrielle', 'is_annuelle']):
            for record in self:
                record._create_intervention_lines()
        return result
