# -*- coding: utf-8 -*-
{
    'name': 'Contrôle qualité Z2S',
    'version': '1.0',
    'summary': 'Module du contrôle qualité pour Z2S',
    'sequence': -2,
    'author': 'BMG Tech',
    'description': """
        Ce module permet la gestion complète du contrôle qualité intégré avec le module nn_Z2S.
        Fonctionnalités principales :
        - Création et suivi des contrôles de qualité liés aux ordres de fabrication
        - Suivi de l’état des contrôles (brouillon, en cours,, terminé)
        - Génération automatique de la référence du contrôle qualité
    """,
    'category': 'Manufacturing',
    'website': 'https://www.bmgtech.tn',
    'depends': ['base','sale','mrp', 'stock', 'nn_Z2S','barcodes','report_xlsx'],
    'data': [
        'security/groups.xml',  # Define access rights for quality control
        'security/ir.model.access.csv',  # Define access rights for quality control
        'reports/report_control_quality_template.xml',
        'reports/control_quality_excel.xml',
        'reports/header_control_quality.xml',  # Main view for quality control
        'views/control_quality_views.xml',  # Main view for quality control
        'views/configuration_reprise_view.xml',  # Main view for quality control
        'views/configuration_type_default_view.xml',  # Main view for quality control
        'views/custom_serial_number_size.xml',  # Main view for quality control
        'views/configuration_type_default2_view.xml',  # Main view for quality control
        'views/mrp_production_dashboard.xml',  # Main view for quality control
        'views/user_form_view.xml',  # Main view for quality control
        'views/production_form_tree_readonly.xml',  # Main view for quality control
    ],

    'assets': {
        'web.assets_backend': [
            'nn_quality_control/static/src/css/custom_styles.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
