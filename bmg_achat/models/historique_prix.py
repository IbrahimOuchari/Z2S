from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state', '=', 'purchase')]
        elif purchase_order_status == 'fait':
            domain += [('state', '=', 'fait')]
        else:
            domain += [('state', '=', ('purchase', 'fait'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,
                                                                                limit=purchase_order_line_record_limit,
                                                                                order='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                'name': line.id,
                'partner_id': line.partner_id.id,
                'user_id': line.order_id.user_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'purchase_order_id': line.order_id.id,
                'purchase_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_total
            })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids

    purchase_price_history_ids = fields.Many2many("purchase.price.history", string="Historique Prix Achat",
                                                  compute="_get_purchase_price_history")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_purchase_price_history(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_history_obj = self.env['purchase.price.history'].sudo()
        purchase_history_ids = []
        domain = [('product_id', 'in', self.product_variant_ids.ids)]
        purchase_order_line_record_limit = int(ICPSudo.get_param('purchase_order_line_record_limit'))
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        if not purchase_order_line_record_limit:
            purchase_order_line_record_limit = 30
        if not purchase_order_status:
            purchase_order_status = 'purchase'
        if purchase_order_status == 'purchase':
            domain += [('state', '=', 'purchase')]
        elif purchase_order_status == 'fait':
            domain += [('state', '=', 'fait')]
        else:
            domain += [('state', '=', ('purchase', 'fait'))]

        purchase_order_line_ids = self.env['purchase.order.line'].sudo().search(domain,
                                                                                limit=purchase_order_line_record_limit,
                                                                                order='create_date desc')
        for line in purchase_order_line_ids:
            purchase_price_history_id = purchase_history_obj.create({
                'name': line.id,
                'partner_id': line.partner_id.id,
                'user_id': line.order_id.user_id.id,
                'product_tmpl_id': line.product_id.product_tmpl_id.id,
                'variant_id': line.product_id.id,
                'purchase_order_id': line.order_id.id,
                'purchase_order_date': line.order_id.date_order,
                'product_uom_qty': line.product_qty,
                'unit_price': line.price_unit,
                'currency_id': line.currency_id.id,
                'total_price': line.price_total
            })
            purchase_history_ids.append(purchase_price_history_id.id)
        self.purchase_price_history_ids = purchase_history_ids

    purchase_price_history_ids = fields.Many2many("purchase.price.history", string="Historique Prix Achat",
                                                  compute="_get_purchase_price_history")


class resConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_order_line_record_limit = fields.Integer(string="Limite des Enregistrements", default=50,
                                                      config_parameter='purchase_order_line_record_limit')
    purchase_order_status = fields.Selection(
        [('purchase', 'Commande d\'Achat'), ('done', 'Fait'), ('both', 'Les deux')],
        string="Historique Prix Basé sur", default="both", config_parameter='purchase_order_status')

    def get_values(self):
        res = super(resConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        purchase_order_line_record_limit = ICPSudo.get_param('purchase_order_line_record_limit')
        purchase_order_status = ICPSudo.get_param('purchase_order_status')
        res.update(
            purchase_order_line_record_limit=int(purchase_order_line_record_limit),
            purchase_order_status=purchase_order_status
        )
        return res


class PurchasePriceHistory(models.Model):
    _name = 'purchase.price.history'
    _description = 'Purchase Price History'

    name = fields.Many2one("purchase.order.line", string="Ligne de BC Achat")
    partner_id = fields.Many2one("res.partner", string="Fournisseur")
    user_id = fields.Many2one("res.users", string="Responsable Achat")
    product_tmpl_id = fields.Many2one("product.template", string="Template Id")
    variant_id = fields.Many2one("product.product", string="Article")
    purchase_order_id = fields.Many2one("purchase.order", string="BC Achat")
    purchase_order_date = fields.Datetime(string="Date BC Achat")
    product_uom_qty = fields.Float(string="Quantité")
    unit_price = fields.Float(string="Prix")
    currency_id = fields.Many2one("res.currency", string="Devise")
    total_price = fields.Monetary(string="Total", digits='Product Price')
