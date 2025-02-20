from odoo import api, fields, models, tools, _

class Company(models.Model):
    _inherit = "res.company"

    compte_bancaire = fields.Char(string="RIB Bancaire")
    banque = fields.Char(string="Banque")
    agence = fields.Char(string="Agence")
    mat_cnss = fields.Char(string="Immatriculation CNSS")