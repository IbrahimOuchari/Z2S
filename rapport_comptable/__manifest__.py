
{
    'name': 'Rapport Comptable Standard',
    'version': '14',
    'category': 'Accounting',
    'author': 'BMG Tech',
    'summary': 'Générer un rapport comptable dans Odoo Tree View, PDF et Excel, avec la nouvelle implémentation de la comptabilité',
    'website': '',
    'depends': ['account', 'report_xlsx', 'bmg_reporting',],
    'data': [
        'security/ir.model.access.csv',
        'data/report_paperformat.xml',
        'data/data_rapport_comptable.xml',
        'data/res_currency_data.xml',
        'report/report_rapport_comptable.xml',
        'views/account_view.xml',
        'views/account_standard.xml',
        'views/rapport_comptable_template_view.xml',
        'views/res_currency_views.xml',
        'wizard/rapport_comptable_view.xml',
    ],

    'installable': True,
    'auto_install': False,

}
