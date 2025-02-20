{
    'name': "BMG Achat",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Achat",
    'version': '14.0',

    'depends': ['base', 'purchase', 'bmg_contact', ],

    'data': [
        'security/ir.model.access.csv',
        'security/achat_security.xml',
        'views/historique_prix.xml',
        'views/demande_prix.xml',
        'report/rfq_report.xml',
        'report/rfq_template.xml',
        'views/purchase_order.xml',
        'views/dernier_prix_achat.xml',
        'views/seq_achat.xml',
        'views/force_invoice.xml',
        # 'views/type_bc.xml',
        'wizard/cancel_reason_da.xml',
        'wizard/cancel_reason_bc.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
