from odoo import models, fields, api

class WizardCancelReason(models.TransientModel):
    _name = 'wizard.cancel.reason.bc'
    _description = 'Wizard to Specify Cancel Reason BC'

    cancel_reason = fields.Text(string="Raison de Refus")
    bc_id = fields.Many2one('sale.order', string="BC")

    def confirm_cancel_reason_bc(self):
        self.ensure_one()
        self.bc_id.write({
            'state': 'rejete',
            'motif_validation_bc': self.cancel_reason
        })
        return {'type': 'ir.actions.act_window_close'}
