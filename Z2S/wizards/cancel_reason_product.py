from odoo import models, fields, api

class WizardCancelReason(models.TransientModel):
    _name = 'wizard.cancel.reason'
    _description = 'Wizard to Specify Cancel Reason'

    cancel_reason = fields.Text(string="Raison de Refus")
    product_id = fields.Many2one('product.template', string="Product")

    def confirm_cancel_reason(self):
        self.ensure_one()
        self.product_id.write({
            'state_product': '0',
            'motif_validation_produit': self.cancel_reason
        })
        return {'type': 'ir.actions.act_window_close'}
