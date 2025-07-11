from datetime import date

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductivityFilterWizardType1(models.TransientModel):
    _name = 'productivity.filter.wizard.type1'
    _description = "Filtre Type 1 par date de création"

    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")

    # Radio button fields for date selection
    date_filter_type = fields.Selection([
        ('date_realisation_of', 'Date de réalisation OF'),
        ('date_creation_cq', 'Date de création CQ')
    ], string="Filtrer par", default='date_creation_cq', required=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")

    def action_filter(self):
        today = date.today()
        domain = []

        # Choose the date field based on radio button selection
        if self.date_filter_type == 'date_realisation_of':
            date_field = 'manu_of.date_realisation'
        else:
            date_field = 'quality_id.start_date'

        if self.date_start and self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', self.date_end)]
        elif self.date_start and not self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', today)]
        elif not self.date_start and self.date_end:
            domain = [(date_field, '<=', self.date_end)]
        else:
            domain = []  # No filter → include everything
        action = self.env.ref('nn_quality_control.action_control_quality_analysis_tree_type1').read()[0]
        action['domain'] = domain
        return action


class ProductivityFilterWizardType2(models.TransientModel):
    _name = 'productivity.filter.wizard.type2'
    _description = "Filtre Type 2 par date de création"

    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")

    # Radio button fields for date selection
    date_filter_type = fields.Selection([
        ('date_realisation_of', 'Date de réalisation OF'),
        ('date_creation_cq', 'Date de création CQ')
    ], string="Filtrer par", default='date_creation_cq', required=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")

    def action_filter(self):
        today = date.today()
        domain = []

        # Choose the date field based on radio button selection
        # Choose the date field based on radio button selection
        if self.date_filter_type == 'date_realisation_of':
            date_field = 'manu_of.date_realisation'
        else:
            date_field = 'quality_id.start_date'

        if self.date_start and self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', self.date_end)]
        elif self.date_start and not self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', today)]
        elif not self.date_start and self.date_end:
            domain = [(date_field, '<=', self.date_end)]
        else:
            domain = []  # No filter → include everything

        action = self.env.ref('nn_quality_control.action_control_quality_analysis_tree_type2').read()[0]
        action['domain'] = domain
        return action


class ProductivityFilterWizardType3(models.TransientModel):
    _name = 'productivity.filter.wizard.type3'
    _description = "Filtre Type 3 par date de création"

    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")

    # Radio button fields for date selection
    date_filter_type = fields.Selection([
        ('date_realisation_of', 'Date de réalisation OF'),
        ('date_creation_cq', 'Date de création CQ')
    ], string="Filtrer par", default='date_creation_cq', required=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")

    def action_filter(self):
        today = date.today()
        domain = []
        # Choose the date field based on radio button selection
        if self.date_filter_type == 'date_realisation_of':
            date_field = 'manu_of.date_realisation'
        else:
            date_field = 'quality_id.start_date'

        if self.date_start and self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', self.date_end)]
        elif self.date_start and not self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', today)]
        elif not self.date_start and self.date_end:
            domain = [(date_field, '<=', self.date_end)]
        else:
            domain = []  # No filter → include everything

        action = self.env.ref('nn_quality_control.action_control_quality_analysis_tree_type3').read()[0]
        action['domain'] = domain
        return action


class ProductivityFilterWizardQuality(models.TransientModel):
    _name = 'productivity.filter.wizard.quality'
    _description = "Filtre Tableau de bord Qualité par date de création"

    date_start = fields.Date(string="Date Début")
    date_end = fields.Date(string="Date Fin")

    # Radio button fields for date selection
    date_filter_type = fields.Selection([
        ('date_realisation_of', 'Date de réalisation OF'),
        ('date_creation_cq', 'Date de création CQ')
    ], string="Filtrer par", default='date_creation_cq', required=True)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_start > rec.date_end:
                raise ValidationError("La date de début ne peut pas être supérieure à la date de fin.")

    def action_filter(self):
        today = date.today()
        domain = []

        # Choose the date field based on radio button selection
        if self.date_filter_type == 'date_realisation_of':
            date_field = 'date_realisation'
        else:  # date_creation_cq
            date_field = 'control_quality_id.start_date'

        if self.date_start and self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', self.date_end)]
        elif self.date_start and not self.date_end:
            domain = [(date_field, '>=', self.date_start), (date_field, '<=', today)]
        elif not self.date_start and self.date_end:
            domain = [(date_field, '<=', self.date_end)]
        else:
            domain = [(date_field, '>=', '1970-01-01'), (date_field, '<=', today)]

        action = self.env.ref('nn_quality_control.action_control_quality_analysis_tree').read()[0]
        action['domain'] = domain
        return action
