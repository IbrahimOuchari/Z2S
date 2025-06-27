# __manifest__.py

{
    'name': 'Ajustement d’Inventaire avec Quantité Zéro',
    'version': '14.0.1.0.0',
    'category': 'Stock',
    'summary': 'Gérer les ajustements d’inventaire avec quantité zéro, ajout de l’état, impression conditionnelle',
    'description': """
    - Détection et validation de saisie avec quantité 0 dans les ajustements d'inventaire
    - Ajout de la colonne "État" dans la vue en liste des produits
    - Bouton conditionnel "Imprimer PDF" affiché si l’état du produit est "Validé"
    - Modèle PDF en attente de design
    """,
    'author': 'Neonara',
    'website': 'https://neonara.digital',
    'license': 'LGPL-3',
    'depends': ['stock', 'nn_Z2S', 'purchase'],
    'data': [
        # 'security/groups.xml',
        # 'security/ir.model.access.csv',
        'views/stock_inventory_line_tree.xml',
        'views/purchase_rfq_form_view.xml',
        'views/stock_inventory_form.xml',
        # 'views/button_stock_inventory_line.xml',
        'views/js_template.xml',
        # 'report/product_pdf_template.xml',  # à activer une fois le template prêt
    ],

    'assets': {
        'web.assets_backend': [
            'nn_stock_zero_qty_adjustment/static/src/js/inventory_line_redirect_controller.js',
            'nn_stock_zero_qty_adjustment/static/src/js/inventory_line_redirect_view.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
