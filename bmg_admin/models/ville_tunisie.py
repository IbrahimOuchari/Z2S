from odoo import fields, models


class CountryState(models.Model):
    _inherit = "res.country.state"

    name = fields.Char(translate=True)
