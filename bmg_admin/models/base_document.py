from odoo import api, fields, models, tools

from odoo.modules import get_resource_path


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    street = fields.Char(related='company_id.street', readonly=True)
    city = fields.Char(related='company_id.city', readonly=True)
    zip = fields.Char(related='company_id.zip', readonly=True)
    country_id = fields.Many2one(related='company_id.country_id', readonly=True)
    company_registry = fields.Char(related='company_id.company_registry', readonly=True)

    compte_bancaire = fields.Char(string="RIB Bancaire", related='company_id.compte_bancaire')
    banque = fields.Char(string="Banque", related='company_id.banque')
    agence = fields.Char(string="Agence", related='company_id.agence')
