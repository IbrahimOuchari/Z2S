from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    total_due = fields.Float(compute="compute_total_due", string="Montant Dû")
    credit_due = fields.Float(compute="_compute_total_credit_due", string="Crédit Dû")

    def compute_total_due(self):
        for record in self:
            total_amount_due = 0.0
            amount_dues = self.env['account.move'].search(
                [('partner_id', '=', record.id), ('move_type', '=', 'out_invoice')])
            for amount_due in amount_dues:
                total_amount_due += amount_due.amount_residual
            record.total_due = total_amount_due
            amount_dues = self.env['account.move'].search(
                [('partner_id', '=', record.id), ('move_type', '=', 'in_invoice')])
            for amount_due in amount_dues:
                total_amount_due += amount_due.amount_residual
            record.total_due = total_amount_due

    def _compute_total_credit_due(self):
        for record in self:
            total_amount_due = 0
            amount_dues = self.env['account.move'].search(
                [('partner_id', '=', record.id), ('move_type', '=', 'out_refund')])
            for amount_due in amount_dues:
                total_amount_due += amount_due.amount_residual
            record.credit_due = total_amount_due
            amount_dues = self.env['account.move'].search(
                [('partner_id', '=', record.id), ('move_type', '=', 'in_refund')])
            for amount_due in amount_dues:
                total_amount_due += amount_due.amount_residual
            record.credit_due = total_amount_due
