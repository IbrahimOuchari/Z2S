from odoo import models, api, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        for mrp in self:
            # Assuming you have 'quantity_done' field and 'forecast_availability' field
            # Adjust field names if different
            for move_lines in mrp.move_raw_ids:
                if move_lines.quantity_done >= move_lines.forecast_availability:
                    raise UserError(_(
                        "Vous ne pouvez pas terminer cette production car le transfert des composants n'est pas encore effectué.\n"
                        "Veuillez d'abord réaliser correctement l'opération de collecte des composants."
                    ))
        # Call super method if check passes
        return super(MrpProduction, self).button_mark_done()
