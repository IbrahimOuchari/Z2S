{
    'name': 'Options Impression Rapport',
    'version': '14',
    'license': 'LGPL-3',
    'summary': """affiche une fenêtre modale avec des options pour imprimer, télécharger ou ouvrir des rapports pdf
""",
    'description': """
       Choisissez l'une des options suivantes lors de l'impression d'un rapport pdf :
         - imprimer. imprimer le rapport pdf directement avec le navigateur
         - Télécharger. télécharger le rapport pdf sur votre ordinateur
         - ouvert. ouvrir le rapport pdf dans un nouvel onglet
         Vous pouvez également définir des options par défaut pour chaque rapport
    """,
    'author': 'BMG Tech',
    'category': 'Productivity',
    'images': ['images/icon.png',
               ],
    'depends': ['web'],
    'data': [
        'views/templates.xml',
        'views/ir_actions_report.xml',
    ],
    'qweb': [
        'static/src/xml/report_pdf_options.xml'
    ],
    'installable': True,
    'auto_install': False,
}
