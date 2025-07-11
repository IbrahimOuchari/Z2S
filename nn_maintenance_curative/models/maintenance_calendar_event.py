from datetime import timedelta

from odoo import models, fields, api


class MaintenanceCalendarEvent(models.Model):
    _name = 'maintenance.calendar.event'
    _description = 'Maintenance Calendar Event'
    _order = 'name asc'  # or just remove this line

    name = fields.Char(string="Nom de la maintenance", required=True)
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string="Équipement",
        required=True,
        ondelete='cascade'
    )
    period_count = fields.Selection([
        ('1', 'Mensuelle'),
        ('2', 'Trimestrielle'),
        ('3', 'Semestrielle'),
        ('4', 'Annuelle'),
    ], string="Fréquence", required=True)

    frequency_days = fields.Integer(string="Fréquence (jours)", required=True)

    technician_user_id = fields.Many2one(
        'res.users',
        string="Technicien",
        related='equipment_id.technician_user_id',
        store=True,
        readonly=True
    )
    start_maintenance_date = fields.Date(
        string="Date de début",
        required=True
    )

    @api.model
    def generate_lines(self, years=2):
        """Generate maintenance calendar event lines for the next `years` years"""
        EventLine = self.env['maintenance.calendar.event.line']
        for event in self.search([]):
            if not event.frequency_days or not event.start_maintenance_date:
                continue

            start_date = event.start_maintenance_date

            # Remove future duplicates
            old_lines = EventLine.search([
                ('event_id', '=', event.id),
                ('date', '>=', start_date)
            ])
            old_lines.unlink()

            days_limit = years * 365
            current_date = start_date
            lines_vals = []

            while (current_date - start_date).days <= days_limit:
                lines_vals.append({
                    'event_id': event.id,
                    'date': current_date,
                })
                current_date += timedelta(days=event.frequency_days)

            if lines_vals:
                EventLine.create(lines_vals)


class MaintenanceCalendarEventLine(models.Model):
    _name = 'maintenance.calendar.event.line'
    _description = 'Ligne de planning maintenance'
    _order = 'date asc'

    event_id = fields.Many2one(
        'maintenance.calendar.event',
        string="Événement de maintenance",
        required=True,
        ondelete='cascade'
    )

    date = fields.Date(string="Date de maintenance", required=True)

    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string="Équipement",
        related='event_id.equipment_id',
        store=True,
        readonly=True,
    )

    period_count = fields.Selection(
        related='event_id.period_count',
        store=True,
        readonly=True,
        string="Fréquence"
    )

    name = fields.Char(string="Nom", compute="_compute_name", store=True)

    @api.depends('event_id.period_count', 'event_id.equipment_id.name')
    def _compute_name(self):
        period_labels = {
            '1': 'Mensuelle',
            '2': 'Trimestrielle',
            '3': 'Semestrielle',
            '4': 'Annuelle',
        }

        for line in self:
            label = period_labels.get(line.period_count, 'Maintenance')
            equip_name = line.equipment_id.name or ''
            line.name = f"{label} maintenance {equip_name}"
