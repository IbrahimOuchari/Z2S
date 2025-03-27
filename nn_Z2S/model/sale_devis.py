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



    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('validation', 'Attente Validation'),
        ('devis', 'Devis Validé'),
        ('confirme', 'Commande'),
        ('nonvalide', 'Non Validé'),
        ('pending_cancellation', 'En attente de confirmation d\'annulation'),
        ('cancel', 'Non Concrétisé'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=True,
        default='draft', store=True)

    def action_confirm_cancellation(self):
        for record in self :
            if record.state == 'pending_cancellation':
                record.state = 'cancel'
                record.devis_cancel_show_div = False


    def action_reject_cancellation(self):
        for record in self:
            if record.state == 'pending_cancellation':
                record.state = 'devis'
                record.devis_cancel = False
                record.devis_cancel_show_div = False


    devis_cancel = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )
    devis_cancel_show_div = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )

    invalidation_reason = fields.Text(string="Raison d'invalidation",
                                      help="Indiquer la raison de l'invalidation")
    date_validation = fields.Datetime(string="Date de Validation")