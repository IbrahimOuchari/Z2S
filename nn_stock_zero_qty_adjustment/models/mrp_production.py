from odoo import models, api, _, fields
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        self.bom_id = False  # Always clear bom_id when product_tmpl_id changes

    def button_mark_done(self):
        for mrp in self:
            for picking in mrp.picking_ids:
                if picking.state != 'done':
                    raise UserError(_(
                        "Vous ne pouvez pas terminer cette production car le transfert des composants n'est pas encore effectué.\n"
                        "Veuillez d'abord réaliser correctement l'opération de collecte des composants."
                    ))
        return super(MrpProduction, self).button_mark_done()
