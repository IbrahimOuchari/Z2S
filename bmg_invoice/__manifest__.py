{
    'name': "BMG Facturation",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Facturation",
    'version': '14.0',

    'depends': ['base', 'account','purchase','sale', 'l10n_tn', 'sale_management', 'Z2S',],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/detail_paiement.xml',
        'views/doc_source_facture.xml',
        'views/montant_paye_liste_facture.xml',
        'views/ligne_facture.xml',
        'views/maj_date_ech.xml',
        'views/details_facture_bc.xml',
        'views/mode_paiement.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}