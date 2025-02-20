
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_back_to_draft(self):
        moves = self.mapped("move_lines")
        moves.action_back_to_draft()
