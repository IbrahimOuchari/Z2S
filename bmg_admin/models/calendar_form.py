from odoo import models, fields, api

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    date_realisation = fields.Datetime(string="Date de Réalisation")
    type_visite = fields.Selection([('prospection', 'Prospection'), ('visite', 'Visite')], string="Type de Visite",
                                    required=True)