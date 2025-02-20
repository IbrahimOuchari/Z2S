from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.exceptions import ValidationError



class StockPickingline(models.Model):
    _inherit = "stock.move"
    _description = "Stock Picking"

    sale_order_line = fields.Many2one()
    sale_id = fields.Many2one()

    @api.constrains('move_lines')
    def _check_quantity_done(self):
        for picking in self:
            for move in picking.move_lines:
                if move.quantity_done <= 0:
                    raise ValidationError("La quantité réalisée doit être supérieure à zéro.")

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.picking_type_code == 'outgoing' and self.operation_fourni != 'retour':
            return {
                'domain': {
                    'product_id': "[('client_id', '=', parent.partner_id), ('sale_ok', '=', True), ('state_product', '=', '1')]"},
            }
        elif self.picking_type_code == 'internal' and self.operation_fourni == 'retour':
            return {
                'domain': {
                    'product_id': "[('client_id', '=', parent.partner_id), '|', ('fourni', '=', True), ('sale_ok', '=', True), ('state_product', '=', '1')]"},
            }
        elif self.picking_type_code == 'incoming' and self.operation_fourni == 'fourni':
            return {
                'domain': {
                    'product_id': "[('client_id', '=', parent.partner_id), ('fourni', '=', True), ('state_product', '=', '1')]"},
            }
        elif self.picking_type_code == 'incoming' and self.operation_fourni != 'fourni':
            return {
                'domain': {
                    'product_id': "[('purchase_ok', '=', True), ('state_product', '=', '1')]"},
            }
        elif self.picking_type_code == 'internal':
            return {
                'domain': {
                    'product_id': "[('state_product', '=', '1')]"},
            }
        else:
            return {
                'domain': {
                    'product_id': []
                },
            }


# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     def button_validate(self):
#         for move in self.move_lines:
#             if move.picking_type_code == 'outgoing' and not move.ref_of:
#                 raise UserError("Veuillez remplir le champ Référence OF.")
#
#         return super(StockPicking, self).button_validate()

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    ref_of = fields.Many2one('mrp.production',
                             string="Ordre de Fabrication",
                             domain="[('product_id', '=', product_id), ('state','=','done'), ('active_livraison','=',False)]",
                             )

    qty_of_reste = fields.Float(related='ref_of.quantite_restante', String="Qty OF", digits='Product Unit of Measure')

    date_done_id = fields.Datetime(related="picking_id.date_done")
    num_bl = fields.Char(related="picking_id.name")
    poste_id = fields.Char(related="move_id.poste_id")
    picking_type_code = fields.Selection(related='move_id.picking_type_code')



    @api.onchange("qty_done")
    def _check_quantity_of(self):
        for line in self:
            if line.qty_done > line.qty_of_reste and line.picking_type_code == "outgoing":
                raise UserError("La quantité introduite est supérieure à celle de l'OF.")

