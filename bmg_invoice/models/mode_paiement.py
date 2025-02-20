from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class payments(models.Model):
    _inherit = 'account.payment'

    payment_mode = fields.Selection(
        selection=[('change', 'Espèce'), ('cheque', 'Chèque'), ('vir', 'Virement'), ('traite', 'Traite')])
    date_ch = fields.Datetime(string="Date Chèque")
    num_ch = fields.Char(string="Numéro de Chèque")
    num_traite = fields.Char(string="Numéro de Traite")
    date_traite = fields.Datetime(string="Date Traite")
    date_vir = fields.Datetime(string="Date Virement")

    @api.onchange('payment_mode')
    def _onchange_payment_mode(self):
        if self.payment_mode == 'change':
            journal = self.env['account.journal'].search([('name', '=', 'Espèces')], limit=1)
            self.journal_id = journal.id if journal else False
        else:
            journal = self.env['account.journal'].search([('name', '=', 'Banque')], limit=1)
            self.journal_id = journal.id if journal else False


class AccountPaymentInherit(models.TransientModel):
    _inherit = 'account.payment.register'

    payment_mode = fields.Selection(
        selection=[('change', 'Espèce'), ('cheque', 'Chèque'), ('vir', 'Virement'), ('traite', 'Traite')])
    date_ch = fields.Datetime(string="Date Chèque")
    num_ch = fields.Char(string="Numéro de Chèque")
    num_traite = fields.Char(string="Numéro de Traite")
    date_traite = fields.Datetime(string="Date Traite")
    date_vir = fields.Datetime(string="Date Virement")

    @api.onchange('payment_mode')
    def _onchange_payment_mode(self):
        if self.payment_mode == 'change':
            journal = self.env['account.journal'].search([('name', '=', 'Espèces')], limit=1)
            self.journal_id = journal.id if journal else False
        else:
            journal = self.env['account.journal'].search([('name', '=', 'Banque')], limit=1)
            self.journal_id = journal.id if journal else False

