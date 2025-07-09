{
    'name': 'Filtre Productivité par Date',
    'version': '14.0.1.0.0',
    'depends': ['nn_Z2S'],
    'author': 'Your Name',
    'category': 'Manufacturing',
    'summary': 'Ajoute un assistant pour filtrer les ordres de fabrication par date de réalisation',
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_productivity_filter_view.xml',
    ],
    'installable': True,
    'application': False,
}
