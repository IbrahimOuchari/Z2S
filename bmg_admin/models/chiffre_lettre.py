from odoo import api, fields, models
from datetime import datetime

class SaleDevis(models.Model):
    _inherit = 'sale.devis'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + '.'

    num_word = fields.Char(string="Arrêtée le Présent Devis à la Somme de : ", compute='_compute_amount_in_word')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + '.'

    num_word = fields.Char(string="Arrêtée la Présente Commande à la Somme de : ", compute='_compute_amount_in_word')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # @api.multi
    def _compute_amount_in_word(self):
        for rec in self:
            # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + '.'

    num_word = fields.Char(string="Arrêtée la Présente Commande à la Somme de : ", compute='_compute_amount_in_word')


class InvoiceOrder(models.Model):
    _inherit = 'account.move'

    num_word = fields.Char(string="Arrêtée la Présente Facture à la Somme de : ", compute='_compute_amount_in_word')

    # @api.multi
    def _compute_amount_in_word(self):
        self.num_word = ""
        for rec in self:
            # rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + ' only'
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + '.'
