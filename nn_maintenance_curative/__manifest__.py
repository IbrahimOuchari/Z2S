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
    'depends': ['base', 'maintenance', 'hr'],
    'data': [
        'security/security_rules_and_groups.xml',
        'security/ir.model.access.csv',
        'data/maintenance_curative_sequence.xml',
        'views/maintenance_curative_form_calendar_views.xml',
        'views/maintenance_equipment_form_view.xml',
        # Ajoutez ici les fichiers XML (vues, actions, séquences, etc.)
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
