# -*- coding: utf-8 -*-

{
    'name': "Masquer bouton Imprimer Action",

    'summary': """
        Bouton Imprimer et Action avec des droits d'accès""",

    'description': """
        Bouton Imprimer et Action avec des droits d'accès dans tous les modules""",

    'author': 'BMG Tech',
    'license': 'LGPL-3',
    # for the full list
    'category': 'Tools',
    'version': '14',
    'support': '',

    'live_test_url': '',

    # any module necessary for this one to work correctly
    'depends': ['base','web'],
    
    'qweb': [
        "static/src/xml/base.xml",
    ],
    # always loaded
    'data': [
        'views/templates.xml',
        'security/security.xml',
    ],
    "images": ['static/description/icon.png'],

}
