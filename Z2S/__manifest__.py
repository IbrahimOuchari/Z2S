{
    "name": "Module Z2S",
    "author": "BMG Tech",
    "version": "14",
    "summary": "Modification différents modules Z2S",

    "depends": [
        "base", "mail", "web", "hr", "contacts", "mrp", "bmg_contact",
        "stock", "mrp", "sale_stock", "bmg_sale", "bmg_stock","bmg_achat",

    ],

    "data": [
        "security/ir.model.access.csv",
        "security/groups.xml",
        "wizards/cancel_reason_product.xml",
        "views/bc_z2s_view.xml",
        "views/livraison.xml",
        # "wizards/select_of_picking.xml",
        "views/livraison_of.xml",
        "views/product_template.xml",
        "views/mrp_product_bom.xml",
        "views/invoice_view.xml",
        "views/mrp_routing_view.xml",
        "views/mrp_gamme_operation.xml",
        "views/hr.xml",
        "views/purchase.xml",
        "views/mrp_product_view.xml",
        # "views/stock_picking_invoice_link.xml",
        "views/filter_product_client_devis.xml",
        "views/ligne_commande.xml",
        "views/ligne_devis.xml",
        "views/product_location_view.xml",
        "reports/template_etiquette_reception.xml",

    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}
