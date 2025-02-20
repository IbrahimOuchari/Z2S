{
    'name': "BMG HR",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies HR",
    'version': '14.0',

    'depends': ['base', 'hr', 'hr_contract', 'hr_recruitment'],

    'data': [
        'security/ir.model.access.csv',
        'views/auto_calcul_age.xml',
        'views/type_contrat.xml',
        'views/document_management.xml',
        'views/skill_qualification.xml',
        'views/matricule.xml',
        'views/duree_service.xml',
        'views/poste_categorie.xml',
        'views/organigramme.xml',
        'views/multi_poste.xml',
    ],

    "qweb": ["static/src/xml/hr_org_chart_overview.xml"],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
