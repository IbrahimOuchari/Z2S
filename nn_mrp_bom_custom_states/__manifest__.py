# -*- coding: utf-8 -*-
{
    'name': 'MRP BOM Custom States',
    'version': '14.0.1.0.0',
    'category': 'Manufacturing',
    'sequence': -2,
    'author': 'Your Name',
    'website': 'https://yourcompany.com',
    'depends': ['stock','Z2S','nn_Z2S'],
    'data': [
        'security/groups.xml',  # Path to your updated form view XML file
        'security/ir.model.access.csv',  # Path to your updated form view XML file
        'views/mrp_bom_states.xml',  # Path to your updated form view XML file
        'views/mrp_production_bom_id.xml',  # Path to your updated form view XML file
        'views/mrp_destruction_bom_id.xml',  # Path to your updated form view XML file
        'wizards/mrp_bom_wizard.xml',  # Path to your updated form view XML file
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'description': """
        This module adds custom states (draft, confirm, rejected, done) 
        to the Bill of Materials (BOM) with French labels.
    """,
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
