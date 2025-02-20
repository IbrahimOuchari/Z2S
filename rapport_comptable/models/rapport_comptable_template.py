# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class AccountStandardLedger(models.Model):
    _name = 'account.report.template'
    _description = 'Account Standard Ledger Template'

    name = fields.Char(default='Standard Report Template')
    ledger_type = fields.Selection(
        [('general', 'Grand Livre Général'),
         ('partner', 'Livre des Tiers'),
         ('journal', 'Journal'),
         ('open', 'Journal Ouevrture'),
         ('aged', 'Balance Âgée'),
         ('analytic', 'Grand Livre Analytique')],
        string='Type', default='general', required=True,
        help=' * General Ledger : Journal entries group by account\n'
        ' * Partner Leger : Journal entries group by partner, with only payable/recevable accounts\n'
        ' * Journal Ledger : Journal entries group by journal, without initial balance\n'
        ' * Open Ledger : Openning journal at Start date\n')
    summary = fields.Boolean('Balance de Vérification', default=False,
                             help=' * Check : generate a trial balance.\n'
                             ' * Uncheck : detail report.\n')
    amount_currency = fields.Boolean('With Currency', help='It adds the currency column on report if the '
                                     'currency differs from the company currency.')
    reconciled = fields.Boolean(
        'Avec des entrées rapprochées', default=True,
        help='Only for entrie with a payable/receivable account.\n'
        ' * Check this box to see un-reconcillied and reconciled entries with payable.\n'
        ' * Uncheck to see only un-reconcillied entries. Can be use only with parnter ledger.\n')
    partner_ids = fields.Many2many(
        comodel_name='res.partner', string='Partenaires',
        domain=['|', ('is_company', '=', True), ('parent_id', '=', False)],
        help='If empty, get all partners')
    account_methode = fields.Selection([('include', 'Include'), ('exclude', 'Exclude')], string="Méthode")
    account_in_ex_clude_ids = fields.Many2many(comodel_name='account.account', string='Comptes',
                                               help='If empty, get all accounts')
    account_group_ids = fields.Many2many(comodel_name='account.group', string='Groupe de Comptes')
    analytic_account_ids = fields.Many2many(comodel_name='account.analytic.account', string='Comptes Analytiques')
    init_balance_history = fields.Boolean(
        'Solde Initial avec Historique', default=True,
        help=' * Check this box if you need to report all the debit and the credit sum before the Start Date.\n'
        ' * Uncheck this box to report only the balance before the Start Date\n')
    company_id = fields.Many2one('res.company', string='Société', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id',
                                          string="Devise", readonly=True,
                                          help='Utility field to express amount currency', store=True)
    journal_ids = fields.Many2many('account.journal', string='Journaux', required=True,
                                   default=lambda self: self.env['account.journal'].search(
                                       [('company_id', '=', self.env.user.company_id.id)]),
                                   help='Select journal, for the Open Ledger you need to set all journals.')
    date_from = fields.Date(string='Date Début', help='Use to compute initial balance.')
    date_to = fields.Date(string='Date Fin', help='Use to compute the entrie matched with futur.')
    target_move = fields.Selection([('posted', 'Toutes les Entrées Publiées'),
                                    ('all', 'All Entries'),
                                    ], string='Mouvements Ciblés', required=True, default='posted')
    result_selection = fields.Selection([('customer', 'Clients'),
                                         ('supplier', 'Fournisseurs'),
                                         ('customer_supplier', 'Client & Fournisseur')
                                         ], string="Sélection Partenaire", required=True, default='supplier')
    report_name = fields.Char('Report Name')
    compact_account = fields.Boolean('Compte compact', default=False)

    @api.onchange('account_in_ex_clude_ids')
    def _onchange_account_in_ex_clude_ids(self):
        if self.account_in_ex_clude_ids:
            self.account_methode = 'include'
        else:
            self.account_methode = False

    @api.onchange('ledger_type')
    def _onchange_ledger_type(self):
        if self.ledger_type in ('partner', 'journal', 'open', 'aged'):
            self.compact_account = False
        if self.ledger_type == 'aged':
            self.date_from = False
            self.reconciled = False
        if self.ledger_type not in ('partner', 'aged',):
            self.reconciled = True
            return {'domain': {'account_in_ex_clude_ids': []}}
        self.account_in_ex_clude_ids = False
        if self.result_selection == 'supplier':
            return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', '=', 'supplier')]}}
        if self.result_selection == 'customer':
            return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', '=', 'customer')]}}
        return {'domain': {'account_in_ex_clude_ids': [('type_third_parties', 'in', ('supplier', 'customer'))]}}
