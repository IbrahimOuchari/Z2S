from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    product_tmpl_id = fields.Many2one(
        'product.template', string='Product Template', required=True,
        help="The template of the product being inventoried."
    )
    # Field to select the product (article)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_ref = fields.Char(
        related='product_id.ref_product_client', string='Référence',
        readonly=True, store=True)

    # Adding fields to track corresponding fields from stock.inventory
    category_id = fields.Many2one('product.category', string='Article Category', related='product_id.categ_id',
                                  store=True)
    partner_id = fields.Many2one('res.partner', string='Client', related='product_id.client_id', store=True)

    client_id = fields.Many2one('res.partner', string='Client', related='product_id.client_id', store=True)
    is_produit_fini = fields.Boolean(string="Produit Fini", related='inventory_id.is_produit_fini', store=True)
    is_produit_achete = fields.Boolean(string="Produit Acheté", related='inventory_id.is_produit_achete', store=True)
    is_produit_fourni = fields.Boolean(string="Produit Fourni", related='inventory_id.is_produit_fourni', store=True)
    exhausted = fields.Boolean(string="Exhausted", related='inventory_id.exhausted', store=True)
    inventory_id = fields.Many2one('stock.inventory', string='Inventory', required=True, ondelete='cascade')

    product_qty_counted = fields.Float(
        string='Product Quantity Counted',
        default=False,  # Allows the field to be empty
        help="Enter the counted quantity. Leave empty if not touched."
    )

    @api.onchange('product_qty_counted')
    def _onchange_product_qty_counted(self):
        """Ensure quantity is non-negative and update product_qty accordingly."""
        for record in self:
            # Check if the new value is non-negative
            if record.product_qty_counted is not False and record.product_qty_counted < 0:
                raise ValidationError("La quantité comptée ne peut pas être négative.")

            # Update product_qty to reflect product_qty_counted
            record.product_qty = record.product_qty_counted

    @api.constrains('product_qty_counted')
    def _check_product_qty_counted(self):
        """Ensure the quantity is either empty or zero/positive."""
        for record in self:
            if record.product_qty_counted < 0:
                raise ValidationError("La quantité comptée ne peut pas être négative.")

    @api.depends('product_id')
    def _onchange_product_id(self):
        """Onchange method to update ref_product_client based on selected product."""
        for record in self:
            if record.product_id:
                # Fetch ref_product_client from the product.template
                record.ref_product_client = record.product_id.product_tmpl_id.ref_product_client
            else:
                # Reset ref_product_client if no product is selected
                record.ref_product_client = False

    can_edit = fields.Boolean(
        string='Compté',
        compute='_compute_can_edit'
    )

    @api.depends('product_qty_counted')
    def _compute_can_edit(self):

        for record in self:

            if self.env.user.has_group('nn_Z2S.stock_inventory_validation'):

                record.can_edit = False

            else:

                record.can_edit = True

    @api.onchange('category_id', 'partner_id', 'is_produit_fini', 'is_produit_achete', 'is_produit_fourni', 'exhausted')
    def _onchange_filter_product_domain(self):
        domain = []

        if self.is_produit_achete:
            domain.append(('purchase_ok', '=', True))

        if self.is_produit_fini:
            domain.append(('sale_ok', '=', True))

        if self.category_id:
            domain.append(('categ_id', '=', self.category_id.id))

        if self.partner_id:
            domain.append(('client_id', '=', self.partner_id.id))

        if self.is_produit_fourni:
            domain.append(('seller_ids', '!=', False))

        if self.exhausted:
            domain.append(('qty_available', '>=', 0))
        else:
            domain.append(('qty_available', '>', 0))

        return {'domain': {'product_id': domain}}

    @api.onchange('inventory_id')
    def _onchange_inventory_id(self):
        if self.inventory_id:
            self.category_id = self.inventory_id.category_id
            self.partner_id = self.inventory_id.partner_id
            self.is_produit_fini = self.inventory_id.is_produit_fini
            self.is_produit_achete = self.inventory_id.is_produit_achete
            self.is_produit_fourni = self.inventory_id.is_produit_fourni
        else:
            self.category_id = False
            self.partner_id = False
            self.is_produit_fini = False
            self.is_produit_achete = False
            self.is_produit_fourni = False
