

{
    'name': "Rapport de facture impayée",
    'author': 'BMG Tech',
    'category': 'account_invoicing',
    'summary': """Rapport sur le montant de la facture impayée par client au cours d'une période définie """,
    'website': '',
    'license': 'AGPL-3',
    'description': """Rapport sur le montant de la facture impayée par client au cours d'une période définie """,
    'version': '14',
    'depends': ['base','account', 'bmg_reporting'],
    'data': ['security/ir.model.access.csv','wizard/invoice_outstanding.xml','views/invoice_outstanding_report_view.xml','report/invoice_outstanding_template.xml','report/invoice_outstanding_report.xml'],
    'installable': True,
    'images': ['static/description/banner.png'],
    'application': True,
    'auto_install': False,
}
