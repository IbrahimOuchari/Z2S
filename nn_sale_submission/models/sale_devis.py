from datetime import date

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleDevis(models.Model):
    _inherit = 'sale.devis'

    def _auto_mark_expired_quotations(self):
        today = date.today()
        expired_orders = self.search([
            ('state', 'in', ['draft', 'sent']),
            ('validity_date', '<', today)
        ])
        for order in expired_orders:
            order.state = 'cancel'  # ou 'cancel' si vous préférez
