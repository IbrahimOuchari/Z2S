# __manifest__.py

{
    'name': 'Collecte des Composants OF',
    'version': '14.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Réservation exclusive des composants lors de la validation d’un OF',
    'description': """
    - À la validation d’un OF, les composants sont réservés uniquement à cet OF
    - Les composants déjà réservés ne peuvent pas être réutilisés dans un autre OF
    - Contrainte empêchant le chevauchement de réservations
    """,
    'author': 'Neonara',
    'website': 'https://neonara.digital',
    'license': 'LGPL-3',
    'depends': ['mrp', 'stock'],
    'data': [
        'views/mrp_production_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
