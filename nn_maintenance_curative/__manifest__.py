{
    'name': "Maintenance Curative",
    'version': '1.0',
    'summary': "Gestion des interventions curatives sur les équipements",
    'description': """
        Ce module permet la gestion des interventions curatives en suivant plusieurs phases :
        - Déclaration de la demande
        - Diagnostic et planification
        - Réalisation
        - Efficacité
        - Clôture
    """,
    'author': "Votre Nom",
    'website': "Votre Site Web",
    'category': 'Maintenance',
    'depends': ['base', 'maintenance', 'hr', 'bmg_sale', 'Z2S'],
    'data': [
        'security/security_rules_and_groups.xml',
        'security/ir.model.access.csv',
        'data/maintenance_curative_sequence.xml',
        'views/maintenance_curative_form_calendar_views.xml',
        'views/maintenance_equipment_form_view.xml',
        'report/maintenance_curative_report.xml',
        'views/maintenance_operation_frequente_view.xml',
        'views/sale_devis_button_fix.xml',
        'views/maintenance_operation_frequente_view.xml',
        'views/maintenance_calendar_view.xml',
        'views/maintenance_request_form.xml',
        'views/product_form_view.xml',
        'views/date_prochaine_maintenance_view.xml',

        # Ajoutez ici les fichiers XML (vues, actions, séquences, etc.)
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'post_init_hook': 'remove_old_model_maintenance_operation_frequente',

}
