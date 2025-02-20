from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sale.price.history'].sudo()
        sale_history_ids = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state', '=', 'sale')]
        elif sale_order_status == 'fait':
            domain += [('state', '=', 'fait')]
        else:
            domain += [('state', '=', ('sale', 'fait'))]

        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain, limit=sale_order_line_record_limit,
                                                                        order='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                'name': line.id,
                'partner_id': line.order_partner_id.id,
                'user_id': line.salesman_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'sale_order_id': line.order_id.id,
                'sale_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_uom_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_subtotal
            })
            sale_history_ids.append(sale_price_history_id.id)
        self.sale_price_history_ids = sale_history_ids

    sale_price_history_ids = fields.Many2many("sale.price.history", string="Historique Prix Vente",
                                              compute="_get_sale_price_history")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_sale_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_history_obj = self.env['sale.price.history'].sudo()
        sale_history_ids = []
        domain = [('product_id', 'in', self.ids)]
        sale_order_line_record_limit = int(ICPSudo.get_param('sale_order_line_record_limit'))
        sale_order_status = ICPSudo.get_param('sale_order_status')
        if not sale_order_line_record_limit:
            sale_order_line_record_limit = 30
        if not sale_order_status:
            sale_order_status = 'sale'
        if sale_order_status == 'sale':
            domain += [('state', '=', 'sale')]
        elif sale_order_status == 'fait':
            domain += [('state', '=', 'fait')]
        else:
            domain += [('state', '=', ('sale', 'fait'))]

        sale_order_line_ids = self.env['sale.order.line'].sudo().search(domain, limit=sale_order_line_record_limit,
                                                                        order='create_date desc')
        for line in sale_order_line_ids:
            sale_price_history_id = sale_history_obj.create({
                'name': line.id,
                'partner_id': line.order_partner_id.id,
                'user_id': line.salesman_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'sale_order_id': line.order_id.id,
                'sale_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_uom_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_subtotal
            })
            sale_history_ids.append(sale_price_history_id.id)
        self.sale_price_history_ids = sale_history_ids

    sale_price_history_ids = fields.Many2many("sale.price.history", string="Historique Prix Vente",
                                              compute="_get_sale_price_history")


class resConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_line_record_limit = fields.Integer(string="Limite des Enregistrements", default=50,
                                                  config_parameter='sale_order_line_record_limit')
    sale_order_status = fields.Selection([('sale', 'Commande de Vente'), ('done', 'Fait'), ('both', 'Les deux')],
                                         string="Historique Prix Basé sur", default="both",
                                         config_parameter='sale_order_status')
    purchase_order_line_record_limit = fields.Integer(string="Limite des Enregistrements", default=50,
                                                      config_parameter='purchase_order_line_record_limit')
    purchase_order_status = fields.Selection(
        [('purchase', 'Commande d\'Achat'), ('done', 'Fait'), ('both', 'Les deux')],
        string="Historique Prix Basé sur", default="both", config_parameter='purchase_order_status')

    def get_values(self):
        res = super(resConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_order_line_record_limit = ICPSudo.get_param('sale_order_line_record_limit')
        sale_order_status = ICPSudo.get_param('sale_order_status')
        res.update(
            sale_order_line_record_limit=int(sale_order_line_record_limit),
            sale_order_status=sale_order_status,
        )
        return res


class SalePriceHistory(models.Model):
    _name = 'sale.price.history'
    _description = 'Sale Price History'

    name = fields.Many2one("sale.order.line", string="Lignes de BC Vente")
    partner_id = fields.Many2one("res.partner", string="Client")
    user_id = fields.Many2one("res.users", string="Chargé Client")
    product_tmpl_id = fields.Many2one("product.template", string="Template Id")
    variant_id = fields.Many2one("product.product", string="Article")
    sale_order_id = fields.Many2one("sale.order", string="BC Vente")
    sale_order_date = fields.Datetime(string="Date BC Vente")
    product_uom_qty = fields.Float(string="Quantité")
    unit_price = fields.Float(string="Prix")
    currency_id = fields.Many2one("res.currency", string="Devise")
    total_price = fields.Monetary(string="Total", digits='Product Price')
