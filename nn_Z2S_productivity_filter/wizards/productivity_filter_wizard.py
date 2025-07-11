from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductivityFilterWizard(models.TransientModel):
    _name = 'productivity.filter.wizard'
    _description = "Filtre des OFs par date de réalisation"

    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")

    def action_filter(self):
        domain = []
        today = fields.Date.today()

        if self.date_start and self.date_end:
            # Both dates selected: filter between start and end
            domain.append(('date_realisation', '>=', self.date_start))
            domain.append(('date_realisation', '<=', self.date_end))

        elif self.date_start and not self.date_end:
            # Only start date selected: filter from start date to today
            domain.append(('date_realisation', '>=', self.date_start))
            domain.append(('date_realisation', '<=', today))

        elif not self.date_start and self.date_end:
            # Only end date selected: fetch records with date_realisation <= end date
            domain.append(('date_realisation', '<=', self.date_end))

        else:
            # No dates selected: fetch all records (no domain)

            # If you want to explicitly fetch all, just leave domain empty:
            domain = []

        action = self.env.ref('nn_Z2S.action_productivity_analysis_tree').read()[0]
        action['domain'] = domain
        return action
