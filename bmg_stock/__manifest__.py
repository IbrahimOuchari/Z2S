{
    'name': "BMG Stock",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Stock",
    'version': '14.0',

    'depends': ['base', 'stock', 'delivery', 'sale_stock', 'sales_team', 'purchase_stock',
                'bmg_sale', 'bmg_achat', 'bmg_admin', 'product'],

    'data': [
        'security/ir.model.access.csv',
        'views/inventaire_update_qty.xml',
        'views/status_livraison_bc.xml',
        'views/livraison_manuelle_vente.xml',
        'wizards/livraison_manuelle_vente_wzd.xml',
        'views/stock_no_negative.xml',
        'views/related_invoice_picking.xml',
        'views/qty_dispo_vente.xml',
        'wizards/reception_manuelle_achat.xml',
        'views/reception_manuelle_achat.xml',
        'views/verrou_emplacement_stock.xml',
        'views/etat_reception.xml',
        'views/dispo_produit.xml',
        'views/stock_vide.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
