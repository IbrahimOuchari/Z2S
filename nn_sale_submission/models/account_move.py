from odoo import models, fields, api
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    amount_residual = fields.Monetary(string='Amount Due', store=True, digits=(16, 10),
                                      compute='_compute_amount')

    @api.onchange('amount_residual')
    def _onchange_amount_residual(self):
        print("Test amount_residual")
        self.payment_state_force_change()
        print("Testfunction called ")

    def payment_state_force_change(self):
        print("Function Started ")

        for rec in self:
            print("Function Started ")

            if rec.amount_residual is not None and rec.amount_residual < 0.0001:
                rec.payment_state = 'paid'
