
{
    "name": "Facturation depuis Inventaire",
    "version": "14",
    "category": "Warehouse Management",
    "author": "BMG Tech",
    "website": "",
    "license": "AGPL-3",
    "depends": ["stock", "account", "stock_picking_invoice_link", "Z2S"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/stock_invoice_onshipping_view.xml",
        "wizards/stock_return_picking_view.xml",
        "views/stock_move.xml",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "demo": ["demo/stock_picking_demo.xml"],
    "installable": True,
}
