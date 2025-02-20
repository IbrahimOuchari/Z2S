{
    'name': "BMG Contact",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Contact",
    'version': '14.0',

    'depends': ['base', 'sale_management', 'purchase', 'contacts'],

    'data': ['security/ir.model.access.csv',
             'wizard/warning_wizard.xml',
             'views/avertissement_factures_retard.xml',
             'views/identification_contact.xml',
             'views/limit_credit_client.xml',
             'views/montant_du.xml',

             ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
