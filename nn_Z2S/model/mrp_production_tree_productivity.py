import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    total_theo_duration = fields.Float(string="Durée théorique totale", compute="_compute_durations", store=True)
    total_real_duration = fields.Float(string="Durée réelle totale", compute="_compute_durations", store=True)
    total_average_productivity = fields.Float(string="Productivité moyenne totale", compute="_compute_durations",
                                              store=True)

    formatted_theo_duration = fields.Char(string="Durée théorique (formatée)", compute="_compute_formatted_durations")
    formatted_real_duration = fields.Char(string="Durée réelle (formatée)", compute="_compute_formatted_durations")

    @api.depends('workorder_ids.duration_expected', 'workorder_ids.real_duration_float', 'workorder_ids.productivity')
    def _compute_durations(self):
        """ Calcule les moyennes des durées et de la productivité sur les ordres de fabrication liés. """
        for production in self:
            workorders = production.workorder_ids

            # Calcul des moyennes en évitant les divisions par zéro
            total_theo = sum(workorders.mapped('duration_expected')) / len(workorders) if workorders else 0.0
            total_real = sum(workorders.mapped('real_duration_float')) / len(workorders) if workorders else 0.0

            production.total_theo_duration = total_theo
            production.total_real_duration = total_real
            production.total_average_productivity = production.productivity

    @api.depends('total_theo_duration', 'total_real_duration')
    def _compute_formatted_durations(self):
        """ Formate les durées en hh:mm:ss """
        for production in self:
            production.formatted_theo_duration = self._format_duration(
                production.total_theo_duration * 60)  # Conversion en secondes
            production.formatted_real_duration = self._format_duration(
                production.total_real_duration * 60)  # Conversion en secondes

    def _extract_seconds_from_duration(self, duration_str):
        """ Convertit une durée formatée (ex: '2H 30M') en secondes """
        total_seconds = 0
        if not duration_str:
            return total_seconds

        try:
            parts = duration_str.split()
            for part in parts:
                if 'H' in part:
                    total_seconds += int(part.replace('H', '').strip()) * 3600
                elif 'M' in part:
                    total_seconds += int(part.replace('M', '').strip()) * 60
                elif 'S' in part:
                    total_seconds += int(part.replace('S', '').strip())
        except Exception as e:
            _logger.error(f"Erreur lors de l'extraction des secondes de '{duration_str}': {e}")

        return total_seconds

    def _format_duration(self, total_seconds):
        """ Convertit un nombre de secondes en format 'XH YM ZS' """
        try:
            if total_seconds <= 0:
                return "0S"

            hours = int(total_seconds // 3600)  # Convert to int to avoid decimals
            minutes = int((total_seconds % 3600) // 60)  # Convert to int to avoid decimals
            seconds = int(total_seconds % 60)  # Convert to int to avoid decimals

            parts = []
            if hours > 0:
                parts.append(f"{hours}H")
            if minutes > 0:
                parts.append(f"{minutes}M")
            if seconds > 0 or (hours == 0 and minutes == 0):  # Always show seconds if no hours/minutes
                parts.append(f"{seconds}S")

            return " ".join(parts)
        except Exception as e:
            _logger.error(f"Erreur lors du formatage de la durée {total_seconds}: {e}")
            return "0S"
