{
    'name': "BMG Sale",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Sale",
    'version': '14.0',

    'depends': ['base', 'sale_management', 'sale', 'bmg_contact', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'report/devis_report.xml',
        'report/devis_template.xml',
        'views/sale_devis.xml',
        'views/sale_order.xml',
        'views/line_description_view.xml',
        'views/notification_invoice.xml',
        'views/remise.xml',
        'views/historique_prix.xml',
        'wizard/cancel_reason_devis.xml',
        'wizard/cancel_reason_bc.xml',
        'views/seq_vente.xml',
        'views/force_invoice.xml',

        'views/devise_produit.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
