from odoo import models, fields, api

class WizardCancelReason(models.TransientModel):
    _name = 'wizard.cancel.reason.da'
    _description = 'Wizard to Specify Cancel Reason DA'

    cancel_reason = fields.Text(string="Raison de Refus")
    da_id = fields.Many2one('purchase.rfq', string="DA")

    def confirm_cancel_reason_da(self):
        self.ensure_one()
        self.da_id.write({
            'state': 'nonvalide',
            'motif_validation_da': self.cancel_reason
        })
        return {'type': 'ir.actions.act_window_close'}
