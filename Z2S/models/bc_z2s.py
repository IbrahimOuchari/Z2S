from odoo import api, fields, models
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Bon de Commande"

    ref_client = fields.Char(string="N° Bon de Commande Client")

    # @api.constrains('ref_client')
    # def _check_unique_ref_client(self):
    #     for record in self:
    #         existing_records = self.search([('ref_client', '=', record.ref_client), ('id', '!=', record.id)])
    #         if existing_records:
    #             raise ValidationError("Le numéro de la commande existe déjà.")

    type_commande = fields.Selection([('type_1', 'HPR'), ('type_2', 'ST')], string="Type de la Commande",
                                     default="type_1", required=True)

    total_sans_remise = fields.Monetary(string='Montant Total', store=True, readonly=True, compute='_total_sans_remise',
                                        tracking=5)

    @api.depends('order_line.prix_remise')
    def _total_sans_remise(self):
        for order in self:
            total_sans_remise = 0.0
            for line in order.order_line:
                total_sans_remise += line.prix_remise
            order.update({
                'total_sans_remise': total_sans_remise,

            })

    class SaleOrdeLine(models.Model):
        _inherit = "sale.order.line"
        _description = "Sales Line Management"

        poste = fields.Char(string="N° Poste")
        ref_product_client_id = fields.Char('product.template', related="product_id.ref_product_client", )

        ref_client_id = fields.Char('sale.order', domain="[('partner_id', '=', partner_id)]",
                                    related="order_id.ref_client")

        status_bc = fields.Selection('sale.order', related="order_id.picking_status")

        prix_remise = fields.Float(string='Total', digits='Product Price', compute="_compute_price_remise")

        pu_avec_remise = fields.Float(string='P.U. Après Remise', digits='Product Price', readonly=True,
                                      compute='_pu_avec_remise', )

        qty_restante = fields.Float(string='Qte Restante', digits='Product Unit of Measure',
                                    compute="_compute_qte_restante")

        @api.depends("product_uom_qty", "qty_delivered")
        def _compute_qte_restante(self):
            for line in self:
                line.qty_restante = line.product_uom_qty - line.qty_delivered

        @api.depends('product_uom_qty', 'price_unit')
        def _compute_price_remise(self):
            for compute in self:
                compute.prix_remise = compute.product_uom_qty * compute.price_unit

        @api.depends('discount', 'price_unit')
        def _pu_avec_remise(self):
            for compute in self:
                compute.pu_avec_remise = ((100 - compute.discount) / 100) * compute.price_unit

    class StockPicking(models.Model):
        _inherit = "stock.picking"

        ref_client_id = fields.Char('sale.order', domain="[('partner_id', '=', partner_id)]",
                                    related="sale_id.ref_client")

        operation_fourni = fields.Selection(related='picking_type_id.operation_fourni')
        currency_id = fields.Many2one('res.currency', string='Currency', related='sale_id.currency_id')

        amount_total = fields.Monetary(string="Montant Total", compute="_compute_total_amount",
                                       currency_field="currency_id")

        @api.depends('move_ids_without_package.total_ligne')
        def _compute_total_amount(self):
            for record in self:
                amount_total = 0.0
                for line in record.move_ids_without_package:
                    amount_total += line.total_ligne
                record.update({
                    'amount_total': amount_total,

                })

    class PickingType(models.Model):
        _inherit = "stock.picking.type"

        operation_fourni = fields.Selection(
            [('fourni', 'Opération Fourni'), ('retour', 'Opération Retour'), ('livraison', 'Opération Livraison')])

    class StockPickingline(models.Model):
        _inherit = "stock.move"
        _description = "Stock Picking"

        picking_type_code = fields.Selection(related='picking_id.picking_type_code')
        operation_fourni = fields.Selection(related='picking_id.operation_fourni')

        price_id = fields.Float(readonly=True, related="sale_line_id.price_unit")
        discount = fields.Float(readonly=True, related="sale_line_id.discount")

        poste_id = fields.Char(readonly=True, related="sale_line_id.poste")
        sale_order_line = fields.Many2one()
        sale_id = fields.Many2one()
        ref_product_client_id = fields.Char('product.template', related="product_id.ref_product_client")
        description_sale_id = fields.Text('product.template', related="product_id.description_sale")
        unit_price = fields.Float(readonly=True, related="sale_line_id.pu_avec_remise")
        currency_id = fields.Many2one('res.currency', string='Currency', related='picking_id.currency_id')
        total_ligne = fields.Monetary("Total", compute="_compute_total_ligne", currency_field="currency_id")

        @api.depends('unit_price', 'quantity_done')
        def _compute_total_ligne(self):
            for line in self:
                line.total_ligne = line.unit_price * line.quantity_done

    class ProductProduct(models.Model):
        _inherit = "product.product"

    client_id = fields.Many2one('product.template', 'product_id.client_id')

    # Ajout pour devis

    class SaleDevisLine(models.Model):
        _inherit = 'sale.devis.line'
        _description = 'Sales Devis Line'

        ref_product_client_id = fields.Char('product.template', related="product_id.ref_product_client")
