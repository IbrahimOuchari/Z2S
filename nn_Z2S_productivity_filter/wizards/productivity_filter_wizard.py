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
        if self.date_start:
            domain.append(('date_realisation', '>=', self.date_start))
        if self.date_end:
            domain.append(('date_realisation', '<=', self.date_end))

        if not self.date_start and not self.date_end:
            domain.append(('id', '=', -1))  # No result

        action = self.env.ref('nn_Z2S.action_productivity_analysis_tree').read()[0]
        action['domain'] = domain
        return action
