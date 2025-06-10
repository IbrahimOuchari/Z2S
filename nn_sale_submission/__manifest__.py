{
    'name': 'Sale Submission Period',
    'version': '14.0.1.0.0',
    'summary': 'Adds submission period fields to sale order and restricts picking validation outside the range',
    'depends': ['sale', 'stock'],
    'author': 'Neonara',
    'category': 'Sales',
    'website': 'https://neonara.digital',
    'data': [
        'views/sale_order_views.xml',
        'reports/stock_picking_report.xml',
    ],
    'installable': True,
    'application': False,
}
