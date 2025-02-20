from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def print_etiquette(self):
        # Assurez-vous qu'il y a un seul enregistrement pour générer le rapport
        self.ensure_one()

        # Récupérez le rapport depuis l'identifiant
        report = self.env.ref('Z2S.action_template_etiquette_reception')

        # Générez le rapport pour l'enregistrement actuel
        return report.report_action(self)

    of_manual = fields.Boolean(default=False, string='Livraison sans OF')


class StockMove(models.Model):
    _inherit = "stock.move"

    colis = fields.Integer(string="Quantité Colis")
