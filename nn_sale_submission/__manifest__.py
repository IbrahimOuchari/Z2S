{
    'name': 'Sale Submission Period',
    'version': '14.0.1.0.0',
    'summary': 'Adds submission period fields to sale order and restricts picking validation outside the range',
    'depends': ['sale', 'stock', ],
    'author': 'Neonara',
    'category': 'Sales',
    'website': 'https://neonara.digital',
    'depends': ['Z2S', 'sale', 'bmg_sale'],
    'data': [
        'views/sale_order_views.xml',
        'reports/stock_picking_report.xml',
        'data/cron_expired_quotation.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
}
