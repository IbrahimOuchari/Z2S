from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def refresh_consumption(self):
        """Refresh raw material consumption (product_uom_qty and quantity_done) based on BoM and product_qty."""
        for production in self:
            if not production.bom_id:
                raise UserError(_("No Bill of Materials (BoM) found for this manufacturing order."))

            # Get the scaling factor based on product_qty and BoM product_qty
            factor = production.product_qty / production.bom_id.product_qty

            for move in production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                old_qty = move.product_uom_qty
                # Find the corresponding BoM line for the raw material
                bom_line = production.bom_id.bom_line_ids.filtered(lambda bl: bl.product_id == move.product_id)

                if bom_line:
                    # Calculate the new quantity based on BoM line quantity and scaling factor
                    new_qty = bom_line.product_qty * factor
                    move.write({'product_uom_qty': new_qty})  # Update the quantity in the stock move

                    # Set the quantity_done to match the product_qty from mrp.production
                    move.write({'quantity_done': production.product_qty})  # Set quantity_done to product_qty

                    move._action_assign()  # Reassign stock reservations (ensures proper allocation)

            return True
