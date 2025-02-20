# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_back_to_draft(self):
        invalid_states = ["cancel", "confirmed", "assigned", "done"]
        if self.filtered(lambda m: m.state not in invalid_states):
            raise UserError(_("Vous ne pouvez pas remettre en Brouillon le Bon "))
        self.write({"state": "draft"})

