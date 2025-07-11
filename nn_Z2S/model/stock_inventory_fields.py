import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

# Set up a logger
_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    category_id = fields.Many2one('product.category', string='Article Category')
    partner_id = fields.Many2one('res.partner', string='Client')
    is_produit_fini = fields.Boolean(string="Produit Fini")
    is_produit_achete = fields.Boolean(string="Produit Acheté")
    is_produit_fourni = fields.Boolean(string="Produit Fourni")
    accounting_date = fields.Date(default=fields.Date.today)
    location_ids = fields.Many2many(
        'stock.location',
        string='Emplacements',
        readonly=True,
        check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id),"
               "('usage', 'in', ['internal', 'transit']),"
               "('scrap_location', '=', False),"
               "('return_location', '=', False)]"
    )

    def _get_location_domain(self):
        usage_list = ['internal', 'transit']
        if self.location_ids.scrap_location:
            usage_list.append('inventory')  # or 'scrap' if needed
        if self.location_ids.return_location:
            usage_list.append('return')  # if Odoo defines it like this

        return [('company_id', '=', self.company_id.id), ('usage', 'in', usage_list)]

    def action_open_inventory_lines(self):
        self.ensure_one()

        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'name': _('Inventory Lines'),
            'res_model': 'stock.inventory.line',
        }

        context = {
            'default_is_editable': True,
            'default_inventory_id': self.id,
            'default_company_id': self.company_id.id,
        }

        domain = self._get_inventory_lines_domain()

        if self.product_ids:
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree_no_product_create').id
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id
        else:
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree').id

        if self.location_ids:
            context['default_location_id'] = self.location_ids[0].id
            if len(self.location_ids) == 1 and not self.location_ids[0].child_ids:
                context['readonly_location_id'] = True

        action['context'] = context
        action['domain'] = domain
        return action

    def _get_inventory_lines_domain(self):
        self.ensure_one()

        domain = [
            ('inventory_id', '=', self.id),
            ('product_id.active', '=', True),
            ('location_id.scrap_location', '=', False),
            ('location_id.return_location', '=', False),
        ]

        # Include newly added lines (is_new=True) OR lines with is_new=False and theoretical_qty >= 0
        domain = ['|',
                  ('is_new', '=', True),
                  '&', ('is_new', '=', False), ('theoretical_qty', '>=', 0)
                  ] + domain

        # Product type filters exactly as in action_open_inventory_lines
        if self.is_produit_fini and not self.is_produit_fourni and not self.is_produit_achete:
            domain += [('product_id.sale_ok', '=', True)]
        elif not self.is_produit_fini and self.is_produit_fourni and not self.is_produit_achete:
            domain += [('product_id.fourni', '=', True)]
        elif not self.is_produit_fini and not self.is_produit_fourni and self.is_produit_achete:
            domain += [('product_id.purchase_ok', '=', True)]
        elif self.is_produit_fini and self.is_produit_fourni and not self.is_produit_achete:
            domain += ['|', ('product_id.sale_ok', '=', True), ('product_id.fourni', '=', True)]
        elif self.is_produit_fini and not self.is_produit_fourni and self.is_produit_achete:
            domain += ['|', ('product_id.sale_ok', '=', True), ('product_id.purchase_ok', '=', True)]
        elif not self.is_produit_fini and self.is_produit_fourni and self.is_produit_achete:
            domain += ['|', ('product_id.fourni', '=', True), ('product_id.purchase_ok', '=', True)]
        elif self.is_produit_fini and self.is_produit_fourni and self.is_produit_achete:
            domain += ['|', '|', ('product_id.sale_ok', '=', True), ('product_id.fourni', '=', True),
                       ('product_id.purchase_ok', '=', True)]

        # Location filter
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        else:
            domain.append(('location_id.usage', 'in', ['internal', 'transit']))

        # Category and partner filters
        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))
        if self.partner_id:
            domain.append('|')
            domain.append(('product_id.client_id', '=', self.partner_id.id))
            domain.append(('is_new', '=', True))

        return domain

    def get_filtered_inventory_lines(self):
        self.ensure_one()

        domain = [
            ('inventory_id', '=', self.id),
            ('product_id.active', '=', True),
            ('location_id.scrap_location', '=', False),
            ('location_id.return_location', '=', False),
        ]
        domain = ['|', ('is_new', '=', True)] + domain

        # ✔️ Keep exact structure, but remove all = False filters

        if self.is_produit_fini and not self.is_produit_fourni and not self.is_produit_achete:
            domain += [
                ('product_id.sale_ok', '=', True),
            ]
        elif not self.is_produit_fini and self.is_produit_fourni and not self.is_produit_achete:
            domain += [
                ('product_id.fourni', '=', True),
            ]
        elif not self.is_produit_fini and not self.is_produit_fourni and self.is_produit_achete:
            domain += [
                ('product_id.purchase_ok', '=', True),
            ]
        elif self.is_produit_fini and self.is_produit_fourni and not self.is_produit_achete:
            domain += [
                '|',
                ('product_id.sale_ok', '=', True),
                ('product_id.fourni', '=', True),
            ]
        elif self.is_produit_fini and not self.is_produit_fourni and self.is_produit_achete:
            domain += [
                '|',
                ('product_id.sale_ok', '=', True),
                ('product_id.purchase_ok', '=', True),
            ]
        elif not self.is_produit_fini and self.is_produit_fourni and self.is_produit_achete:
            domain += [
                '|',
                ('product_id.fourni', '=', True),
                ('product_id.purchase_ok', '=', True),
            ]
        elif self.is_produit_fini and self.is_produit_fourni and self.is_produit_achete:
            domain += [
                '|', '|',
                ('product_id.sale_ok', '=', True),
                ('product_id.fourni', '=', True),
                ('product_id.purchase_ok', '=', True),
            ]
        else:
            # No filters selected — optional fallback
            pass

        # Filter by selected locations if any
        if self.location_ids:
            domain.append(('location_id', 'in', self.location_ids.ids))
        else:
            domain.append(('location_id.usage', 'in', ['internal', 'transit']))

        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))
        if self.partner_id:
            domain.append(('product_id.client_id', '=', self.partner_id.id))

        # Return all matching lines
        return self.env['stock.inventory.line'].search(domain)

    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'In Progress'),
        ('demand_close', 'Demande Clôture inventaire'),
        ('done', 'Validated')],
                             copy=False, index=True, readonly=True, tracking=True,
                             default='draft')

    inventory_cancel = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )
    invalidation_reason = fields.Text(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )

    def reject_inventory(self):
        """Set `inventory_cancel` to True, revert state to 'confirm', and open wizard."""
        return {
            'name': "Rejeter l'Inventaire",
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.cancel.inventory',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_inventory_id': self.id,
            },
        }

    def action_print_count(self):
        return self.env.ref('nn_Z2S.action_report_count_sheet').report_action(self)

    inventory_line_ids = fields.One2many(
        'stock.inventory.line',  # Related model
        'inventory_id',  # Inverse field
        string='Inventory Lines'
    )
    label_management = fields.Many2one('label.management', string="Label Management")

    def print_stock_inventory_line(self):
        # Ensure there is only one record to generate the report
        self.ensure_one()

        # Fetch the report from the identifier
        report = self.env.ref('nn_Z2S.action_template_stock_inventory_line_print')

        # Generate the report for the associated Label Management records
        # You might want to filter the LabelManagement records related to this production order
        return report.report_action(self.mapped('inventory_line_ids'))


class StockInventoryLineTrigger(models.Model):
    _inherit = 'stock.inventory.line'

    def action_trigger_demand_close(self):
        inventory = self.inventory_id
        inventory.action_confirm_zero_qty()

    # def action_reconfirm_zero_qty(self):
    #     # Get the inventory linked to this line
    #     inventory = self.inventory_id
    #
    #     # Find lines with zero quantity
    #     zero_qty_lines = self.env['stock.inventory.line'].search([
    #         ('inventory_id', '=', inventory.id),
    #         ('product_qty_counted', '=', 0)
    #     ])
    #
    #     # If there are lines with zero quantity, show a confirmation message
    #     if zero_qty_lines:
    #         raise UserError(
    #             _("Il y a encore des lignes avec une quantité égale à zéro. Êtes-vous sûr de vouloir continuer ?")
    #         )
    #         inventory.action_confirm_zero_qty()
    #
    #     # Proceed with the state change in stock.inventory
    #     # inventory.action_confirm_zero_qty()


class ResCompany(models.Model):
    _inherit = 'res.company'

    log_afaq = fields.Binary(string="Logo AFAQ")


class UpdateStockQuantFIx(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        # Check if location_id and product_id already exist in the quant
        location_id = vals.get('location_id')
        product_id = vals.get('product_id')
        quantity = vals.get('quantity', 0)

        # Search for existing quants with the same location and product
        existing_quant = self.search([
            ('location_id', '=', location_id),
            ('product_id', '=', product_id),
        ], limit=1)

        if existing_quant:
            # If existing quant found, merge quantities
            existing_quant.quantity += quantity
            return existing_quant  # Return the existing quant, no new quant created
        else:
            # If no existing quant, create a new one
            return super(UpdateStockQuantFIx, self).create(vals)

    def write(self, vals):
        # Check if location_id or product_id is being changed
        if 'location_id' in vals or 'product_id' in vals:
            # In case of a change in location or product, we need to merge with the new quant
            location_id = vals.get('location_id', self.location_id.id)
            product_id = vals.get('product_id', self.product_id.id)
            quantity = vals.get('quantity', self.quantity)

            # Search for existing quants with the same location and product
            existing_quant = self.search([
                ('location_id', '=', location_id),
                ('product_id', '=', product_id),
            ], limit=1)

            if existing_quant:
                # If existing quant found, merge quantities
                existing_quant.quantity += quantity
                return existing_quant.write(vals)  # Merge quantities and return the updated quant
        # If no merge needed, proceed with the usual write behavior
        return super(UpdateStockQuantFIx, self).write(vals)
