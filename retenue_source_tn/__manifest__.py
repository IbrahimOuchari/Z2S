{
    'name': "BMG Retenue à la Source",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Retenue à la Source",
    'version': '14.0',

    'depends': ['base', 'account', 'bmg_invoice'],

    'data': ['security/ir.model.access.csv',
             'views/partner_view.xml',
             'views/account_tax_view.xml',
             'views/account_move_view.xml',
             'views/account_payment_view.xml',
             'wizard/account_payment_register_view.xml',
             'report/ras_report.xml',
             'report/ras_template.xml',
             'report/ras_template_facture.xml',

             ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}