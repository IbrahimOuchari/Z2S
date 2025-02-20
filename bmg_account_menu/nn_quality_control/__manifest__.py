# -*- coding: utf-8 -*-
{
    'name': 'Contrôle qualité Z2S',
    'version': '1.0',
    'summary': 'Module de gestion du contrôle qualité pour Z2S',
    'sequence': 10,
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
    'depends': ['base', 'mrp', 'stock', 'nn_Z2S'],  # Updated dependencies
    'data': [
        'security/ir.model.access.csv',  # Define access rights for quality control
        'reports/report_control_quality_template.xml',
        'views/control_quality_views.xml',  # Main view for quality control
        'views/configuration_reprise_view.xml',  # Main view for quality control
        'views/configuration_type_default_view.xml',  # Main view for quality control
    ],
    'installable': True,
    'application': False,  # Not a full application
    'auto_install': False,
    'license': 'LGPL-3',
}
