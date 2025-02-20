
from odoo import fields, models


class AccountAccountTag(models.Model):
    _inherit = "account.account.tag"

    account_ids = fields.Many2many(
        comodel_name="account.account",
        relation="account_account_account_tag",
        string="Accounts",
    )
