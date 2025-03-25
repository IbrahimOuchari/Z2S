from odoo import fields , models , api



class SaleDevis(models.Model):
    _inherit = 'sale.devis'


    def action_cancel(self):
        return {
            'name': "Devis Perdu",
            'type': 'ir.actions.act_window',
            'res_model': 'devis.perdu.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_devis_id': self.id, },
        }

    devis_cancel = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )

    invalidation_reason = fields.Text(string="Raison d'invalidation",
                                      help="Indiquer la raison de l'invalidation")
    date_validation = fields.Datetime(string="Date de Validation")