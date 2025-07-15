# -*- coding: utf-8 -*-
{
    'name': 'Tourney Quality Control',
    'version': '1.0',
    'summary': 'Module for managing quality control processes within Tourney production.',
    'description': """
        This module provides a comprehensive system for managing quality control at various stages 
        of the production process, including documentary, operational, and product controls.
    """,
    'category': 'Manufacturing/Quality',
    'author': 'Tourney Team',
    'website': 'https://www.tourney.com',  # Replace with your actual website
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mrp',  # Dependency for Manufacturing Orders (mrp.production)
        'product',  # Dependency for product.product (Article)
        'contacts',  # Dependency for res.partner (Client)
        'nn_quality_control',  # 'mail', # Uncomment if you plan to use messaging/activity features
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/tourney_quality_sequence.xml',
        'views/mrp_production_views_inherit.xml',
        'views/tourney_quality_views.xml',
        'views/configuration_doc_operational_menu.xml',
        'views/config_doc.xml',
        'views/config_op.xml',
        # 'views/tourney_quality_views.xml',
        # 'views/tourney_quality_documentary_line_views.xml',
        # 'views/tourney_quality_operational_line_views.xml',
        # 'views/tourney_quality_product_line_views.xml',
        # You might also need to add views for mrp.production if you're adding fields there
        # 'views/mrp_production_views_inherit.xml',
    ],
    'demo': [
        # 'demo/tourney_quality_demo.xml', # Uncomment and create demo data if needed
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
