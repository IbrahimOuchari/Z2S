{
    'name': "BMG Reporting",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Reporting",
    'version': '14.0',

    'depends': ['base', 'bmg_achat', 'bmg_admin', 'bmg_invoice', 'bmg_sale', 'bmg_stock',
                'date_range', 'report_xlsx_helper', 'account', 'product_margin',],

    'data': [
        'security/ir.model.access.csv',
        'wizard/reporting_top_vente_produit.xml',
        'views/top_vente_produit.xml',
        'views/produit_par_fournisseur.xml',
        'views/rapport_stock.xml',
        'views/rapport_vente_commercial.xml',
        'wizard/rapport_vente_commercial.xml',
        'wizard/rapport_produit_pdf.xml',
        'views/rapport_produit_top_vente_view.xml',
        'views/rapport_produit_top_vente_template.xml',
        'views/menu.xml',
        'views/rapport_fiche_stock.xml',
        'wizard/rapport_fiche_stock.xml',



    ],


    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
