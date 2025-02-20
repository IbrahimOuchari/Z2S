from unittest.mock import DEFAULT

from freezegun.api import real_time
from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from datetime import date

import logging

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
        # Define domains and context
        domain = [
            ('inventory_id', '=', self.id),
            ('location_id.usage', 'in', ['internal', 'transit']),
            ('location_id.name', 'not in', ['Retour', 'Destruction']),  # Corrected here
            ('product_id.active', '=', True),  # Corrected here
        ]

        if self.location_ids:
            context['default_location_id'] = self.location_ids[0].id
            if len(self.location_ids) == 1:
                if not self.location_ids[0].child_ids:
                    context['readonly_location_id'] = True

        if self.is_produit_fini:
            domain.append(('product_id.sale_ok', '=', True))

        if self.is_produit_fourni:
            domain.append(('product_id.fourni', '=', True))

        if self.is_produit_achete:
            domain.append(('product_id.purchase_ok', '=', True))

        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))

        if self.partner_id:
            domain.append(('product_id.client_id.id', '=', self.partner_id.id))

        if self.product_ids:
            # no_create on product_id field
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree_no_product_create').id
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id
        else:
            # no product_ids => we're allowed to create new products in tree
            action['view_id'] = self.env.ref('stock.stock_inventory_line_tree').id

        action['context'] = context
        action['domain'] = domain
        return action

    def get_filtered_inventory_lines(self):
        self.ensure_one()
        domain = [
            ('inventory_id', '=', self.id),
            ('location_id.usage', 'in', ['internal', 'transit']),
            ('location_id.name', 'not in', ['Retour', 'Destruction']),  # Corrected here
            ('product_id.active', '=', True),  # Corrected here
        ]
        # Add additional domain filters based on the current record
        if self.is_produit_fini:
            domain.append(('product_id.sale_ok', '=', True))

        if self.is_produit_fourni:
            domain.append(('product_id.fourni', '=', True))

        if self.is_produit_achete:
            domain.append(('product_id.purchase_ok', '=', True))

        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))

        if self.partner_id:
            domain.append(('product_id.client_id', '=', self.partner_id.id))

        # Return a recordset of stock.inventory.line
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

    # def action_demand_close(self):
    #     for record in self:
    #         record.state = 'demand_close'
    #
    #

    def action_demand_close(self):
        self.ensure_one()

        # Define domain for zero quantity lines, including the exclusion of the "Retour" location
        domain = [
            ('inventory_id', '=', self.id),
            ('product_qty_counted', '=', 0),
            ('location_id.name', '!=', 'Retour')  # Exclude location named "Retour"
        ]

        # Define the base context
        context = {
            'default_inventory_id': self.id,
            'default_company_id': self.company_id.id,
        }

        # Additional context and domain logic (same as action_open_inventory_lines)
        if self.location_ids:
            # Filter locations to exclude "Retour" before setting default_location_id
            valid_locations = self.location_ids.filtered(lambda l: l.name != 'Retour')
            if valid_locations:
                context['default_location_id'] = valid_locations[0].id
                if len(valid_locations) == 1:
                    if not valid_locations[0].child_ids:
                        context['readonly_location_id'] = True

        if self.is_produit_fini:
            domain.append(('product_id.sale_ok', '=', True))

        if self.is_produit_fourni:
            domain.append(('product_id.fourni', '=', True))

        if self.is_produit_achete:
            domain.append(('product_id.purchase_ok', '=', True))

        if self.category_id:
            domain.append(('product_id.categ_id', '=', self.category_id.id))

        if self.partner_id:
            domain.append(('product_id.client_id.id', '=', self.partner_id.id))

        # Select appropriate view
        if self.product_ids:
            action_view_id = self.env.ref('stock.stock_inventory_line_tree_no_product_create').id
            if len(self.product_ids) == 1:
                context['default_product_id'] = self.product_ids[0].id
        else:
            action_view_id = self.env.ref('stock.stock_inventory_line_tree').id

        # Check if zero quantity lines exist
        zero_qty_lines = self.env['stock.inventory.line'].search(domain)
        if zero_qty_lines:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'name': _('Lignes avec Quantité Comptée à Zéro'),
                'res_model': 'stock.inventory.line',
                'domain': [('id', 'in', zero_qty_lines.ids)],
                'view_id': action_view_id,
                'target': 'new',
                'context': context,
            }

        # If no zero quantity lines, change the state
        self.state = 'demand_close'

    @api.model
    def action_confirm_zero_qty(self):
        for record in self:
            # Ensure state is changed only after confirmation
            if record.state != 'demand_close':
                record.state = 'demand_close'
                # Optionally, you can log a message or action here
                _logger.info("State updated to 'demand_close' for inventory %s", record.name)
            else:
                raise UserError(_("L'inventaire est déjà clôturé."))

    def action_validate(self):
        if not self.exists():
            return
        self.ensure_one()
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'demand_close':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory "
                "has been already validated or isn't ready.", self.name))
        inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot',
                                                                                     'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
        lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1,
                                                               precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
        if inventory_lines and not lines:
            wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in
                         inventory_lines.mapped('product_id')]
            wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'res_id': wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True

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
