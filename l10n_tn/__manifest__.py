{
    'name': 'Tunisie - Accounting',
    'author': 'BMG Tech',
    'website': 'www.bmgtech.tn',

    'version': '14',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
This is the module to manage the accounting chart for Tunisia in Odoo.
========================================================================
""",
    'depends': [
        'account',
    ],
    'data': [
        'data/l10n_tn_chart_data.xml',
        'data/account.account.template.csv',
        'data/account.group.template.csv',
        'data/account_chart_template_data.xml',
        'data/account_data.xml',
        'data/tax_report_data.xml',
        'data/account_tax_data.xml',
        'data/account_fiscal_position_template_data.xml',
        'data/account_reconcile_model_template.xml',
        'data/account_chart_template_configure_data.xml',
        'views/timbre_fiscal.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

