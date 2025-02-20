from odoo import models, fields, api

#identification contact module contact

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string='Client',
                                 help="Cochez cette case si ce contact est un client.")
    is_supplier = fields.Boolean(string='Fournisseur',
                                 help="Cochez cette case si ce contact est un fournisseur.")

#identification contact module vente

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     partner_id = fields.Many2one(
#         'res.partner', string='Client', readonly=True,
#         states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
#         required=True, change_default=True, tracking=True,
#         domain="['|',('customer_rank','>', 0),('is_customer','=',True)]",)
#
# #identification contact module achat
#
# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     READONLY_STATES = {
#         'purchase': [('readonly', True)],
#         'done': [('readonly', True)],
#         'cancel': [('readonly', True)],
#     }
#
#     partner_id = fields.Many2one(
#         'res.partner', string='Fournisseur', required=True,
#         states=READONLY_STATES, change_default=True,
#         tracking=True, domain="['|',('supplier_rank','>', 0),('is_supplier','=',True)]",
#         help="Vous pouvez rechercher un fournisseur par son nom, son adresse e-mail ou sa référence interne.")
