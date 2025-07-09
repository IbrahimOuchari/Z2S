import logging
from re import match

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
        string="Comptée User",
        help="Saisie utilisateur même pour zéro. Converti automatiquement vers le champ réel."
    )

    @api.constrains('product_qty_counted_char')
    def _check_numeric_input(self):
        for line in self:
            val = line.product_qty_counted_char
            if val and val.strip():
                # Allow numbers with optional decimal (either , or .), no letters
                if not match(r'^\s*-?\d+([.,]\d+)?\s*$', val.strip()):
                    raise ValidationError(
                        _("Le champ 'Quantité Comptée (Texte)' n'accepte que des valeurs numériques. Exemple : 12, 12.5 ou 12,5"))

    product_qty_counted = fields.Float(
        compute='_compute_qty_char',
        store=True
    )

    value_confirmed = fields.Boolean(
        string="Valeur Confirmé",
        # compute='_compute_value_confirmed',
        store=True,
        default=False
    )

    @api.onchange('product_qty_counted_char')
    def _onchange_product_qty_counted_char(self):
        for line in self:
            if line.product_qty_counted_char and line.product_qty_counted_char.strip():
                try:
                    # If text is present, it's used
                    line.product_qty = float(line.product_qty_counted_char.strip())
                    line.value_confirmed = True
                except ValueError:
                    line.product_qty = 0.0
                    line.value_confirmed = False
            else:
                # If text is empty, value is not confirmed
                line.value_confirmed = False

    def _generate_moves(self):
        vals_list = []
        for line in self:
            virtual_location = line._get_virtual_location()
            rounding = line.product_id.uom_id.rounding

            # ✅ Skip only if difference is zero and not confirmed
            if float_is_zero(line.difference_qty, precision_rounding=rounding) and not line.value_confirmed:
                continue

            # ✅ If difference is exactly 0 but confirmed, simulate a tiny move
            qty = abs(line.difference_qty)
            if float_is_zero(qty, precision_rounding=rounding) and line.value_confirmed:
                qty = rounding  # minimum qty based on UoM

            if line.difference_qty > 0 or (line.difference_qty == 0 and line.value_confirmed):
                # Found more than expected or confirmed zero
                vals = line._get_move_values(qty, virtual_location.id, line.location_id.id, False)
            else:
                # Found less than expected
                vals = line._get_move_values(qty, line.location_id.id, virtual_location.id, True)

            vals_list.append(vals)

        return self.env['stock.move'].create(vals_list)

    def action_open_inventory(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Inventaire',
            'view_mode': 'form',
            'res_model': 'stock.inventory',
            'res_id': self.inventory_id.id,
            'target': 'current',
        }

    @api.model
    def create(self, vals):
        record = super(StockInventoryLine, self).create(vals)

        # Only flag as is_new if product_id is being set manually (user input)
        if vals.get('product_id') and self.env.context.get('default_inventory_id'):
            record.is_new = True

        return record

    is_new = fields.Boolean(default=False)
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

    product_qty_counted_char_access = fields.Boolean(
        string='Compté',
        compute='_compute_product_qty_counted_char_access'
    )

    @api.depends('product_qty_counted')
    def _compute_product_qty_counted_char_access(self):

        for record in self:

            if self.env.user.has_group('nn_Z2S.stock_inventory_validation'):

                record.product_qty_counted_char_access = False

            else:
                record.product_qty_counted_char_access = True
