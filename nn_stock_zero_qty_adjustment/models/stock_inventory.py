from odoo import _
from odoo import models, _, fields
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

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

    def action_demand_close(self):
        for record in self:
            domain = record._get_inventory_lines_domain()
            domain.append(('value_confirmed', '=', False))

            unconfirmed_lines = self.env['stock.inventory.line'].search(domain)
            count_unconfirmed = len(unconfirmed_lines)

            if count_unconfirmed:
                message = _(
                    "Il y a %d ligne(s) non confirmée(s). Veuillez les confirmer avant de clôturer l'inventaire."
                ) % count_unconfirmed
                raise UserError(message)

            record.state = 'demand_close'

    def action_show_location_article_counts(self):
        self.ensure_one()

        if not self.location_ids:
            raise UserError(_("Veuillez sélectionner au moins un emplacement."))

        # Get list of relevant locations including children
        domain_loc = [('id', 'child_of', self.location_ids.ids)]
        locations = self.env['stock.location'].search(domain_loc)

        location_ids = locations.ids

        domain = [
            ('company_id', '=', self.company_id.id),
            ('location_id', 'in', location_ids),
        ]
        if not self.exhausted:
            domain.append(('quantity', '>', 0))
        else:
            domain.append(('quantity', '>=', 0))

        quants = self.env['stock.quant'].read_group(
            domain,
            ['product_id', 'location_id'],
            ['product_id', 'location_id'],
            lazy=False,
        )

        # Group products per location (no duplicates)
        location_to_products = {}
        for q in quants:
            loc_id = q['location_id'][0]
            prod_id = q['product_id'][0]
            location_to_products.setdefault(loc_id, set()).add(prod_id)

        # Build the output
        message_lines = []
        for loc in locations:
            count = len(location_to_products.get(loc.id, set()))
            message_lines.append(f"{loc.name} : {count} article(s)")

        raise UserError(_("Nombre d’articles par emplacement :\n\n%s") % "\n".join(message_lines))
