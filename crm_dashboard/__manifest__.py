{
    'name': "BMG CRM Dashbord",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies Tableau de bord CRM",
    'version': '14.0',
    'depends': ['base', 'sale_management', 'crm', 'bmg_reporting'],
    'data': [
        'views/dashboard_view.xml',
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/dashboard_view.xml',
        'static/src/xml/sub_dashboard.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
     'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
