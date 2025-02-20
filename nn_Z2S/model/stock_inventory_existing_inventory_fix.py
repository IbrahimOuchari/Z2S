from odoo.exceptions import UserError, ValidationError
from odoo import _, models, fields
import logging

_logger = logging.getLogger(__name__)

class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    def _check_no_duplicate_line(self):
        domain = [
            ('product_id', 'in', self.product_id.ids),
            ('location_id', 'in', self.location_id.ids),
            '|', ('partner_id', 'in', self.partner_id.ids), ('partner_id', '=', None),
            '|', ('package_id', 'in', self.package_id.ids), ('package_id', '=', None),
            '|', ('prod_lot_id', 'in', self.prod_lot_id.ids), ('prod_lot_id', '=', None),
            '|', ('inventory_id', 'in', self.inventory_id.ids), ('inventory_id', '=', None),
        ]
        groupby_fields = ['product_id', 'location_id', 'partner_id', 'package_id', 'prod_lot_id', 'inventory_id']
        lines_count = {}
        for group in self.read_group(domain, ['product_id'], groupby_fields, lazy=False):
            key = tuple([group[field] and group[field][0] for field in groupby_fields])
            lines_count[key] = group['__count']
        for line in self:
            key = (line.product_id.id, line.location_id.id, line.partner_id.id, line.package_id.id, line.prod_lot_id.id, line.inventory_id.id)
            if lines_count[key] > 1:
                raise UserError(_("There is already one inventory adjustment line for this product,"
                                  " you should rather modify this one instead of creating a new one."))
