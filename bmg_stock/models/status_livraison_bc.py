from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_livre = fields.Float("Total Livraison", compute="_compute_total_livraison")

    def _compute_total_livraison(self):
        for record in self:
            record.total_livre = sum(record.order_line.mapped('qty_delivered'))

    total_commande = fields.Float("Total Commande", compute="_compute_total_commande")

    def _compute_total_commande(self):
        for record in self:
            record.total_commande = sum(record.order_line.mapped('product_uom_qty'))

    livraison_done = fields.Float(default=False, string="Livraison Complète", compute="_compute_livraison_done")

    def _compute_livraison_done(self):
        for record in self:
            record.livraison_done = record.total_commande - record.total_livre

    livraison_complete = fields.Boolean(default=False, string="Livraison Complète",
                                        compute="_compute_livraison_complete")

    @api.depends('livraison_done')
    def _compute_livraison_complete(self):
        for record in self:
            record.livraison_complete = record.livraison_done == 0.00
        print("livraison")

    picking_status = fields.Selection(
        [
            ("done", "Entièrement Livré"),  # order done
            ("in_progress", "En Cours"),  # order in progress
        ],
        string="Livraison",
        copy=False,
        tracking=True,
        index=True,
        compute="_compute_picking_status",
        search="_search_picking_status",
    )

    @api.depends('livraison_complete', 'livraison_done')
    def _compute_picking_status(self):
        for record in self:
            if record.livraison_complete:
                record.picking_status = "done"
            else:
                record.picking_status = "in_progress"
            print("status")

    def _search_picking_status(self, operator, value):
        orders = self.search([("state", "!=", "cancel")])
        f_orders = orders.filtered(lambda x: x.picking_status == value)
        res = [("id", "in", f_orders.ids if f_orders else False)]
        return res
