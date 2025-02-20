
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate_amount = fields.Float(
        string="Taux de Change", compute="_compute_currency_rate_amount", digits=(3,3),
    )
    show_currency_rate_amount = fields.Boolean(
        compute="_compute_show_currency_rate_amount", readonly=True
    )

    @api.depends(
        "state",
        "date",
        "line_ids.amount_currency",
        "company_id",
        "currency_id",
        "show_currency_rate_amount",
    )
    def _compute_currency_rate_amount(self):
        """ It's necessary to define value according to some cases:
        - Case A: Currency is equal to company currency (Value = 1)
        - Case B: Move exist previously (posted) and get real rate according to lines
        - Case C: Get expected rate (according to date) to show some value in creation.
        """
        self.currency_rate_amount = 1
        for item in self.filtered("show_currency_rate_amount"):
                if item.show_currency_rate_amount:
                    rates = item.env['res.currency'].search([('name', '=', 'TND')])
                    item.currency_rate_amount = rates.rate
                else:
                    item.currency_rate_amount = 2


    @api.depends("currency_id", "currency_id.rate_ids", "company_id")
    def _compute_show_currency_rate_amount(self):
        for item in self:
            item.show_currency_rate_amount = (
                item.currency_id and item.currency_id != "TND"
            )


    montant_dt = fields.Float(digits=(3,3), string="Montant en DT", store=True, compute="_compute_montant_dt")

    tva = fields.Float(digits=(3,3), string="Montant TVA", store=True, compute="_compute_tva")


    @api.depends('amount_total', 'currency_rate_amount', 'show_currency_rate_amount')
    def _compute_montant_dt(self):
        for rec in self:
            if rec.show_currency_rate_amount:
                rec.montant_dt = rec.amount_total * rec.currency_rate_amount
            else:
                rec.montant_dt = 0

    @api.depends('montant_dt', 'currency_rate_amount', 'show_currency_rate_amount')
    def _compute_tva(self):
        for rec in self:
            if rec.show_currency_rate_amount:
                rec.tva = (rec.montant_dt * 0.19)
            else:
                rec.tva = 0