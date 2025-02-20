from odoo import models, fields, api

class WizardCancelReasonBCAchat(models.TransientModel):
    _name = 'wizard.cancel.reason.bc.achat'
    _description = 'Wizard to Specify Cancel Reason BC'

    cancel_reason = fields.Text(string="Raison de Refus")
    bc_id = fields.Many2one('purchase.order', string="BC Achat")

    def confirm_cancel_reason_bc_achat(self):
        self.ensure_one()
        self.bc_id.write({
            'state': 'rejete',
            'motif_validation_bc': self.cancel_reason
        })
        return {'type': 'ir.actions.act_window_close'}

