from odoo import models, fields, api

class WizardCancelReason(models.TransientModel):
    _name = 'wizard.cancel.reason.devis'
    _description = 'Wizard to Specify Cancel Reason Devis'

    cancel_reason = fields.Text(string="Raison de Refus")
    devis_id = fields.Many2one('sale.devis', string="Devis")

    def confirm_cancel_reason_devis(self):
        self.ensure_one()
        self.devis_id.write({
            'state': 'nonvalide',
            'motif_validation_devis': self.cancel_reason
        })
        return {'type': 'ir.actions.act_window_close'}
