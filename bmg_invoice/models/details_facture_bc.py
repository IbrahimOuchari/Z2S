from odoo import api, fields, models, _


class SaleOrderUpdate(models.Model):
    _inherit = 'sale.order'

    invoiced_amount = fields.Float(string='Montant Facturé', digits='Product Price', compute='_compute_invoice_amount')
    amount_due_id = fields.Float(string='Montant Restant', digits='Product Price', compute='_compute_amount_due')
    paid_amount = fields.Float(string='Montant Payé', digits='Product Price', compute='_compute_amount_paid')
    amount_paid_percent = fields.Float(compute='action_amount_paid', )
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.user.company_id.currency_id)

    def _compute_invoice_amount(self):
        for record in self:
            invoice_id = self.env['account.move'].search \
                (['&', ('invoice_origin', '=', record.name), '|', ('state', '=', 'draft'), ('state', '=', 'posted')
                     , ('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            total = 0

            if invoice_id:
                for invoice in invoice_id:
                    total += invoice.amount_total
                    record.invoiced_amount = total
            else:
                record.invoiced_amount = total

    @api.depends('paid_amount', 'invoiced_amount', 'amount_due_id')
    def _compute_amount_due(self):
        for record in self:
            invoice_ids = self.env['account.move'].search \
                (['&', ('invoice_origin', '=', record.name), '|', ('state', '=', 'draft'), ('state', '=', 'posted')
                     , ('payment_state', 'not in', ['reversed', 'invoicing_legacy'])])
            amount = 0

            if invoice_ids:
                for inv in invoice_ids:
                    amount += inv.amount_residual
                    record.amount_due_id = amount
            else:
                record.amount_due_id = amount

    @api.onchange('invoiced_amount', 'amount_due_id')
    def _compute_amount_paid(self):
        for record in self:
            record.paid_amount = float(record.invoiced_amount) - float(record.amount_due_id)

    @api.depends('paid_amount', 'invoiced_amount')
    def action_amount_paid(self):
        if self.invoiced_amount:
            self.amount_paid_percent = round(100 * self.paid_amount / self.invoiced_amount, 1)
        return self.amount_paid_percent

    @api.depends('paid_amount', 'invoiced_amount')
    def _compute_payment_status(self):
        for record in self:
            if record.paid_amount == 0:
                record.payment_status = 'not_paid'
            elif record.paid_amount == record.invoiced_amount:
                record.payment_status = 'paid'
            else:
                record.payment_status = 'partial'

    payment_status = fields.Selection(
        selection=[
            ("not_paid", "Impayé"),
            ("paid", "Payé"),
            ("partial", "Partiellement Payé"),
        ],
        string="Statut Paiement",
        readonly=True,
        copy=False,
        tracking=True,
        compute="_compute_payment_status",
    )
