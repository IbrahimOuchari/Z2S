
from odoo import models, fields, api

class StockPickingEdit(models.Model):
    _inherit = 'stock.picking'

    date_done = fields.Datetime('Date Transfère', copy=False, readonly=False, help="Date à laquelle le transfert a été traité ou annulé.")

    scheduled_date = fields.Datetime(
        'Date Prévue', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, default=fields.Datetime.now, tracking=True,
        states={'done': [('readonly', False)], 'cancel': [('readonly', False)]},
        help="Heure prévue pour le traitement de la première partie de l'envoi. La définition manuelle d'une valeur ici la définirait comme date prévue pour tous les mouvements de stock.")

    def _set_scheduled_date(self):
        for picking in self:
#            if picking.state in ('done', 'cancel'):
#                raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_lines.write({'date': picking.scheduled_date})
