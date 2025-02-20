{
    'name': "BMG CRM",
    'author': 'BMG Tech',
    'category': '',
    'summary': """""",
    'license': 'AGPL-3',
    'website': 'www.bmgtech.tn',
    'description': "Modules BMG Technologies CRM",
    'version': '14.0',

    'depends': ['base', 'crm', 'sale_crm', 'bmg_sale', 'sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/probabilite_etape.xml',
        'wizards/probabilite_etape_wizard.xml',
        'data/probabilite_etape.xml',
        'views/ajout_produit.xml',
        'views/instruction_etape.xml',
        'views/stage_change.xml',
        'views/crm_lead.xml',

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
