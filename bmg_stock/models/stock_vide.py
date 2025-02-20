from psycopg2 import sql

from odoo import fields, models, api, exceptions


class StockLocation(models.Model):
    _inherit = "stock.location"

    stock_amount = fields.Float(
            string="Quantité en Stock",
        )

#     stock_amount = fields.Float(
#         compute="_compute_location_amount", search="_search_location_amount", string="Quantité en Stock",
#     )
#
#     def _search_location_amount(self, operator, value):
#         if operator not in ("=", "!=", "<", "<=", ">", ">="):
#             return []
#         query = sql.SQL(
#             """
#             SELECT loc.id FROM stock_location loc
#             LEFT OUTER JOIN stock_quant quant ON loc.id = quant.location_id
#             GROUP BY loc.id
#             HAVING coalesce(sum(quantity), 0) {operator} %(value)s;""".format(
#                 operator=operator
#             )
#         )
#
#         self.env.cr.execute(query, {"value": value})
#         res = self.env.cr.fetchall()
#         ids = [row[0] for row in res]
#         return [("id", "in", ids)]
#
#     def _compute_location_amount(self):
#         query = sql.SQL(
#             """
#             SELECT location_id, sum(quantity)
#             FROM stock_quant
#             WHERE location_id IN %(values)s
#             GROUP BY location_id;
#         """
#         )
#         self.env.cr.execute(query, {"values": tuple(self.ids)})
#         totals = dict(self.env.cr.fetchall())
#         for location in self:
#             location.stock_amount = totals.get(location.id, 0)
#
    allow_multiple_products = fields.Boolean(string="Autoriser plusieurs produits")
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     class StockPicking(models.Model):
#         _inherit = 'stock.picking'
#
#         @api.model
#         def create(self, vals):
#             if 'location_dest_id' in vals:
#                 location_dest_id = vals.get('location_dest_id')
#                 location = self.env['stock.location'].browse(location_dest_id)
#                 # Vérifier si l'emplacement de destination est occupé, sauf si l'emplacement autorise plusieurs produits
#                 if not location.allow_multiple_products:
#                     quants = self.env['stock.quant'].search([('location_id', '=', location_dest_id)])
#                     if quants:
#                         raise exceptions.UserError(
#                             "Vous ne pouvez pas créer une entrée en stock dans un emplacement de destination occupé.")
#
#             return super().create(vals)
