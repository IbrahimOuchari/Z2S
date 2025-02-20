from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class MrpBomCustomState(models.Model):
    _inherit = 'mrp.bom'

    # Adding a custom state field with French labels
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('waiting_for_validation', 'En Attente de Validation') , # New state added

        ('rejected', 'Rejeté'),
        ('done', 'Validé'),
    ], string='État', default='draft', required=True)

    bom_cancel = fields.Boolean(
        string="Raison d'invalidation",
        help="Indiquer la raison de l'invalidation"
    )

    invalidation_reason = fields.Text(string="Raison d'invalidation",
                                      help="Indiquer la raison de l'invalidation")
    date_validation = fields.Datetime(string="Date de Validation")

    def confirm_bom(self):
        for record in self:
            record.state = 'confirm'

    def action_demand_validation_request(self):
        for record in self:
            record.state = 'waiting_for_validation'
            # Set the date_validation field to the current date and time
            record.date_validation = fields.Datetime.now()


    def accept_bom(self):
        for record in self:
            record.state = 'done'

    def reject_bom(self):
        return {
            'name': "Rejeter Nomenclature",
            'type': 'ir.actions.act_window',
            'res_model': 'bom.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_bom_id': self.id, },
        }
