import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError


class ReportProductsAmount(models.AbstractModel):
    _name = 'report.rapport_produit_top_vente.report_products_amount'
    _description = "Report Products Amount"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_records = {}
        sorted_product_records = []
        sales = self.env['sale.order'].search([('state', 'in', ('sale', 'done')), ('date_order', '>=', docs.start_date),
                                               ('date_order', '<=', docs.end_date)])
        for s in sales:
            orders = self.env['sale.order.line'].search([('order_id', '=', s.id)])
            for order in orders:
                if order.product_id:
                    if order.product_id not in product_records:
                        product_records.update({order.product_id: 0})
                    product_records[order.product_id] += order.price_subtotal

        for product_id, price_subtotal in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True)[
                                          :docs.no_of_products]:
            sorted_product_records.append({'name': product_id.name, 'amount': int(price_subtotal),
                                           'pricelist_id': self.env.user.company_id.currency_id})
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'products': sorted_product_records
        }

class ReportProducts(models.AbstractModel):
    _name = 'report.rapport_produit_top_vente.report_products'
    _description = "Report Products"

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_records = {}
        sorted_product_records = []
        sales = self.env['sale.order'].search([('state','in',('sale','done')),('date_order','>=',docs.start_date),('date_order','<=',docs.end_date)])
        for s in sales:
            orders = self.env['sale.order.line'].search([('order_id','=',s.id)])
            for order in orders:
                if order.product_id:
                    if order.product_id not in product_records:
                        product_records.update({order.product_id:0})
                    product_records[order.product_id] += order.product_uom_qty

        for product_id, product_uom_qty in sorted(product_records.items(), key=lambda kv: kv[1], reverse=True)[:docs.no_of_products]:
            sorted_product_records.append({'name':product_id.name, 'qty': int(product_uom_qty)})

        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'docs': docs,
            'time': time,
            'products': sorted_product_records
        }
