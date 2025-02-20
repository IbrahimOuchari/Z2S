# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module Z2S V2 ',
    'version': '2.0',
    'summary': 'Enhanced version  of Module Z2S with improved features ',
    'sequence': -1,
    'author': 'BMG Tech - Upgraded',
    'description': "Advanced version of BMG Technologies module for enhanced commission management.",
    'category': 'Accounting/Accounting',
    'website': 'https://www.bmgtech.tn',
    'depends': ['base', 'mrp', 'product', 'stock', 'sale', 'account', 'Z2S','ks_percent_field'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/stock_inventory_form_tree_view.xml',
        'reports/report_lot_template.xml',
        'reports/stock_inventory_comparison_report.xml',
        'reports/stock_inventory_count_sheet_report.xml',
        'reports/label_management_line_print.xml',
        'reports/label_management_stock_moves_line_print.xml',
        'reports/report_lot_template_stock_picking.xml',
        'views/operation_duree_view.xml',
        'views/custom_mrp_workorder_views.xml',
        'views/mrp_stock_move_componants.xml',
        'views/mrp_production_views.xml',
        'views/productivity_dashboard_view.xml',
        # 'views/productivity_dashboard.xml',
        'views/inventory_freeze.xml',
        'views/stock_inventory_form_tree_view.xml',
        'views/mrp_ordre_fabrication_hide_fields.xml',
        'views/mrp_production_work_order_fix.xml',
        # 'views/mrp_workorder_hide_fields.xml',
        'views/stock_move_from_quantity_left.xml',
        'views/account_move_line_pu.xml',
        # 'views/product_template_quantity_per_batch.xml',
        'views/stock_move_operation_lot.xml',
        'views/stock_picking_lot_button.xml',
        'views/label_management_sequence.xml',
        'views/product_form_view_open_inventory_line.xml',
        'wizards/return_components_wizard_view.xml',
        'wizards/inventory_cancel_wizard.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'nn_Z2S/static/src/js/empty_float_field.js',  # Path to your JS file
        ],
    },
    'images': ['static/src/img/free.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
