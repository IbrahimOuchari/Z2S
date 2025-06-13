# -*- coding: utf-8 -*-
{
    'name': 'Stock Management Enhancements',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Enhanced stock management with custom features',
    'description': """
        This module adds several enhancements to the stock management:
        - Add submission number to delivery slip report
        - Auto labels for "Buy" and "Return" transfers
        - Add location field to inventory count report
        - Handle zero quantity inventory adjustments
        - Add state column to product tree view
        - Conditional PDF print button for validated products
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['stock', 'purchase', 'sale', 'nn_Z2S'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/stock_labels_data.xml',
        # 'views/stock_picking_views.xml',
        # 'views/stock_inventory_views.xml',
        # 'reports/delivery_slip_report.xml',
        # 'reports/inventory_count_report.xml',
        # 'reports/product_pdf_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
