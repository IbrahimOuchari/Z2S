
from odoo import api, fields, models, _

class ProductDetail(models.TransientModel):
    _name = "product.detail"
    _description = "Product Detail"


    start_date = fields.Date(string="Date Début", required='1')
    end_date = fields.Date(string="Date Fin", required='1')
    top_products = fields.Selection([
        ('by_units', 'Unité'),
        ('by_amounts', 'Valeurs')
    ], string='Par', default = 'by_units')
    no_of_products = fields.Integer(string='Nombre de Produit à Afficher', default = '5')

    def check_report(self):
        data = {}
        data['form'] = self.read(['start_date', 'end_date', 'top_products', 'no_of_products'])[0]
        return self._print_report(data)


    def _print_report(self, data):
        data['form'].update(self.read(['start_date', 'end_date', 'top_products', 'no_of_products'])[0])
        if data['form']['top_products'] == 'by_units':
            return self.env.ref('rapport_produit_top_vente.action_report_products').report_action(self, data=data, config=False)
        else:
            return self.env.ref('rapport_produit_top_vente.action_report_products_amount').report_action(self, data=data, config=False)
