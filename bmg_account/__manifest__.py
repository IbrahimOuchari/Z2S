{
    'name': "BMG Rapports Financier",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Rapports Financier",
    'version': '14.0',

    'depends': ['base', 'bmg_invoice', 'account', 'bmg_reporting', 'rapport_facture_imp', 'bmg_account_menu',
               'rapport_comptable', ],

    'data': [
        'security/ir.model.access.csv',
        'views/liste_paiement_du.xml',
        'views/data_rapport_paiement.xml',
        'wizards/rapport_paiement.xml',



    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
