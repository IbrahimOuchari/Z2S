import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    product_qty_counted_char = fields.Char(
        string="Quantité Comptée (Texte)",
        help="Saisie utilisateur même pour zéro. Converti automatiquement vers le champ réel."
    )

    product_qty_counted = fields.Float(
        compute='_compute_qty_char',
        store=True
    )

    confirmed_zero = fields.Boolean(
        string="Zéro Confirmé",
        compute='_compute_confirmed_zero',
        store=True,
        default=False
    )

    @api.depends('product_qty_counted_char')
    def _compute_confirmed_zero(self):
        for line in self:
            if line.product_qty_counted_char:
                if float(line.product_qty_counted_char or 0.0) == line.theoretical_qty:
                    line.confirmed_zero = True
                else:
                    line.confirmed_zero = False

    def _generate_moves(self):
        vals_list = []
        for line in self:
            virtual_location = line._get_virtual_location()
            rounding = line.product_id.uom_id.rounding

            # ✅ Skip only if difference is zero and not confirmed
            if float_is_zero(line.difference_qty, precision_rounding=rounding) and not line.confirmed_zero:
                continue

            # ✅ If difference is exactly 0 but confirmed, simulate a tiny move
            qty = abs(line.difference_qty)
            if float_is_zero(qty, precision_rounding=rounding) and line.confirmed_zero:
                qty = rounding  # minimum qty based on UoM

            if line.difference_qty > 0 or (line.difference_qty == 0 and line.confirmed_zero):
                # Found more than expected or confirmed zero
                vals = line._get_move_values(qty, virtual_location.id, line.location_id.id, False)
            else:
                # Found less than expected
                vals = line._get_move_values(qty, line.location_id.id, virtual_location.id, True)

            vals_list.append(vals)

        return self.env['stock.move'].create(vals_list)
