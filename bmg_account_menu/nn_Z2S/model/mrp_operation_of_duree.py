from odoo import models, fields, api, exceptions
from datetime import timedelta

class MrpOperationOf(models.Model):
    _inherit = 'mrp.operation.of'

    heure_debut = fields.Datetime(string="Heure Début")
    heure_fin = fields.Datetime(string="Heure Fin")
    duree_formatted = fields.Char(string="Durée Formatée", compute="_compute_duree_formatted", store=True)

    @api.constrains('heure_debut', 'heure_fin')
    def _check_dates(self):
        for record in self:
            if record.heure_debut and record.heure_fin:
                delta = record.heure_fin - record.heure_debut
                total_seconds = delta.total_seconds()
                total_hours = total_seconds / 3600

                if record.heure_fin < record.heure_debut:
                    raise exceptions.ValidationError(
                        f"L'heure de fin ({record.heure_fin.strftime('%Y-%m-%d %H:%M:%S')}) "
                        f"ne peut pas être inférieure à l'heure de début ({record.heure_debut.strftime('%Y-%m-%d %H:%M:%S')})."
                    )

                if total_hours > 10:
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    raise exceptions.ValidationError(
                        f"La durée entre l'heure de début ({record.heure_debut.strftime('%Y-%m-%d %H:%M:%S')}) "
                        f"et l'heure de fin ({record.heure_fin.strftime('%Y-%m-%d %H:%M:%S')}) est de "
                        f"{hours} heures et {minutes} minutes, ce qui dépasse la limite autorisée de 10 heures."
                    )

    @api.depends('heure_debut', 'heure_fin')
    def _compute_duree_formatted(self):
        for record in self:
            if record.heure_debut and record.heure_fin:
                try:
                    delta = record.heure_fin - record.heure_debut
                    total_seconds = delta.total_seconds()

                    # Calculate hours, minutes, and seconds
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    seconds = int(total_seconds % 60)

                    # Prepare the formatted string, omitting zero values
                    parts = []
                    if hours > 0:
                        parts.append(f"{hours}H")
                    if minutes > 0:
                        parts.append(f"{minutes}M")
                    if seconds > 0:
                        parts.append(f"{seconds}S")

                    # Join the parts, or show "0" if all are zero
                    record.duree_formatted = " ".join(parts) if parts else "Aucune Durée"

                except Exception as e:
                    record.duree_formatted = "Erreur de calcul"
