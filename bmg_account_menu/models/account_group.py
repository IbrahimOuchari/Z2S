
from odoo import fields, models


class AccountGroup(models.Model):
    _inherit = "account.group"

    account_ids = fields.One2many(
        comodel_name="account.account",
        inverse_name="group_id",
        string="Accounts",
    )
