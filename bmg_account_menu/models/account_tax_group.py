
from odoo import fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    tax_ids = fields.One2many(
        comodel_name="account.tax",
        inverse_name="tax_group_id",
        string="Taxes",
    )
