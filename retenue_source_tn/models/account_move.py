from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, date_utils, email_split, email_re
from odoo.tools.misc import formatLang, format_date, get_lang
from collections import defaultdict


class AccountMove(models.Model):
    _inherit = "account.move"

    # BMG
    date_retenue = fields.Date(string="Date Retenue")
    ras_executed = fields.Boolean(string="Calcul RAS", compute="compute_ras")
    ras_apply = fields.Boolean(string="Appliquer RAS", default=True)
    ras_tax = fields.Boolean(string="RAS", related="ras_apply")
    withholding_tax = fields.Many2one('account.tax', string="Taux RAS",
                                      domain=[("withholding_tax", "=", True)])

    @api.depends('amount_total', 'ras_executed')
    def compute_ras(self):
        for compute in self:

            if compute.amount_total >= 1000 and compute.ras_apply:
                compute.ras_executed = True
            else:
                compute.ras_executed = False

    @api.onchange('ras_apply')
    def onchange_ras_apply(self):
        if self.ras_apply:
            self.ras_executed = True
        else:
            self.ras_executed = False

    @api.onchange('withholding_tax')
    def onchange_withholding_tax(self):
        if self.withholding_tax:
            self.ras_tax = True
        else:
            self.ras_tax = False

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.apply_ras:
            self.ras_tax = True
        else:
            self.ras_tax = False

        tax_ids = []
        if self.partner_id.apply_ras and self.partner_id.withholding_tax:
            if not self.partner_id.withholding_tax.invoice_repartition_line_ids:
                raise ValidationError(
                    _("Attention, veuillez configurer le compte dans Taxe/Retenue à la source (%s, %s)" % (
                        self.partner_id.withholding_tax.id, self.partner_id.withholding_tax.name or "")))
            for tax in self.partner_id.withholding_tax.invoice_repartition_line_ids:
                if not tax.account_id and tax.repartition_type == 'tax':
                    raise ValidationError(
                        _("Attention, veuillez configurer le compte dans Taxe/Retenue à la source (%s, %s)" % (
                            self.partner_id.withholding_tax.id, self.partner_id.withholding_tax.name or "")))

            self.update({
                # 'withholding_tax': [(6, 0, tax_ids)]
                'withholding_tax': self.partner_id.withholding_tax
            })
        else:
            self.withholding_tax = False

        # BMG

    amount_withholding = fields.Monetary(string="Retenue à la Source", digits='Product Price',
                                         compute='_compute_invoice_withholding_taxes', store=True)
    wht_executed = fields.Boolean(string="WHT Executed")

    @api.depends('line_ids.withholding_tax', 'line_ids.withholding_tax_id')
    def _compute_invoice_withholding_taxes(self):
        for move in self:
            if move.invoice_line_ids:
                move.amount_withholding = sum(rec.withholding_subtotal for rec in move.invoice_line_ids)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    withholding_tax = fields.Boolean(string="Application Retenue", related="move_id.ras_executed")
    withholding_tax_id = fields.Many2one('account.tax', string="Retenue",
                                         related="move_id.withholding_tax")
    withholding_subtotal = fields.Monetary(string="Sous Total Retenue", digits='Product Price',
                                           compute='_compute_withholding_subtotal')

    @api.onchange('withholding_tax_id')
    def onchange_withholding_tax_id(self):
        if self.withholding_tax_id:
            if not self.withholding_tax_id.invoice_repartition_line_ids:
                raise ValidationError(
                    _("Attention, veuillez configurer le compte dans Taxe/Retenue à la source (%s, %s)" % (
                        self.product_id.withholding_tax_id.id, self.product_id.withholding_tax_id.name or "")))
            for tax in self.withholding_tax_id.invoice_repartition_line_ids:
                if not tax.account_id and tax.repartition_type == 'tax':
                    raise ValidationError(
                        _("Attention, veuillez configurer le compte dans Taxe/Retenue à la source (%s, %s)" % (
                            self.product_id.withholding_tax_id.id, self.product_id.withholding_tax_id.name or "")))

    @api.depends('quantity', 'price_unit', 'withholding_tax', 'withholding_tax_id', 'discount')
    def _compute_withholding_subtotal(self):
        for rec in self:
            if rec.withholding_tax and rec.withholding_tax_id:
                tax = rec.withholding_tax_id
                amount = rec.quantity * rec.price_unit
                remise = amount * (1 - (rec.discount * 0.01) )
                ttc = remise + (remise * rec.tax_ids.amount * 0.01)
                retenue = ttc * (tax.amount * 0.01)

                rec.withholding_subtotal = retenue
            else:
                rec.withholding_subtotal = 0


class WithholdingLine(models.Model):
    _name = 'withholding.line'

    payment_id = fields.Many2one('account.payment', string="Account Payment")
    account_id = fields.Many2one('account.account', string="Account")
    name = fields.Char(string="Label")
    amount_withholding = fields.Float(string="Amount", digits='Product Price')


class PartnerTemplate(models.Model):
    _inherit = "res.partner"

    apply_ras = fields.Boolean(string="Appliquer RAS")
    withholding_tax = fields.Many2one('account.tax', string="Retenue à la Source",
                                      domain=[("withholding_tax", "=", True)])
