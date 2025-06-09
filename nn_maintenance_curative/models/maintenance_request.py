from odoo import fields, api, models


class InheritMaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    serial_no = fields.Char(related='equipment_id.serial_no', string="SN")
