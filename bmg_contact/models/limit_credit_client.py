from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessDenied


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_check = fields.Boolean('Activer Limitation de Crédit', help='Activer la fonctionnalité de limite de crédit')
    credit_warning = fields.Monetary('Montant Avertissement', digits='Product Price')
    credit_blocking = fields.Monetary('Montant de blocage', digits='Product Price')
    amount_due = fields.Monetary('Montant Dû', compute='_compute_amount_due', digits='Product Price')

    @api.depends('credit')
    def _compute_amount_due(self):
        for rec in self:
            rec.amount_due = rec.credit

    @api.constrains('credit_warning', 'credit_blocking')
    def _check_credit_amount(self):
        for credit in self:
            if credit.credit_warning > credit.credit_blocking:
                raise ValidationError(_('Le montant avertissement ne doit pas être supérieur au montant de blocage.'))
            if credit.credit_warning < 0 or credit.credit_blocking < 0:
                raise ValidationError(
                    _('Le montant avertissement ou le montant de blocage ne doit pas être inférieur à zéro.'))


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_due = fields.Monetary(related='partner_id.amount_due', currency_field='company_currency_id', digits='Product Price')
    company_currency_id = fields.Many2one(string='Devise', readonly=True,
                                          related='company_id.currency_id')

    def action_confirm(self):
        partner_id = self.partner_id
        total_amount = self.amount_due
        if partner_id.credit_check:
            existing_move = self.env['account.move'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'posted')])
            if partner_id.credit_blocking <= total_amount and not existing_move:
                view_id = self.env.ref('limite_credit_client.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context[
                    'message'] = "Limite de blocage client dépassée sans avoir de paiement, voulez-vous continuer ?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Attention',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_warning <= total_amount and partner_id.credit_blocking > total_amount:
                view_id = self.env.ref('limite_credit_client.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context['message'] = "Limite d'avertissement client dépassée, voulez-vous continuer ?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_blocking <= total_amount:
                raise AccessDenied(_('Limite de crédit client dépassée.'))
        res = super(SaleOrder, self).action_confirm()
        return res
