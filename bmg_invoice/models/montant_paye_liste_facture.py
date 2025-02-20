
from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = "Montant Payé Liste des Facture"

    paid_amount = fields.Monetary(string='Montant Payé', compute='_compute_paid_amount', store=True, help="Montant payé", digits='Product Price')

    @api.depends('amount_residual')
    def _compute_paid_amount(self):
        for inv in self:
            inv.paid_amount = 0.0
            if inv.state != 'draft':
                inv.paid_amount = inv.amount_total - inv.amount_residual
