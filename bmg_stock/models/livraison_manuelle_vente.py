from odoo import fields, models, api, _
from odoo.exceptions import UserError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    manual_delivery = fields.Boolean(
        string="Livraison Manuelle",
        help="Si activé, les livraisons ne sont pas créées lors de la confirmation du SO. "
             "Vous devez utiliser le bouton Créer une livraison pour réserver et "
             "expédier la marchandise.",
        default=True,
    )


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    date_planned = fields.Date()


class SaleOrder(models.Model):
    _inherit = "sale.order"

    manual_delivery = fields.Boolean(
        string="Livraison Manuelle",
        default=True,
        help="Si activé, les livraisons ne sont pas créées lors de la confirmation du SO. "
             "Vous devez utiliser le bouton Créer une livraison pour réserver et "
             "expédier la marchandise",
    )

    @api.onchange("team_id")
    def _onchange_team_id(self):
        self.manual_delivery = self.team_id.manual_delivery

    def action_manual_delivery_wizard(self):
        self.ensure_one()
        action = self.env.ref("bmg_stock.action_wizard_manual_delivery")
        [action] = action.read()
        action["context"] = {"default_carrier_id": self.carrier_id.id}
        return action

    @api.constrains("manual_delivery")
    def _check_manual_delivery(self):
        if any(rec.state not in ["brouillon", "sale"] for rec in self):
            raise UserError(
                _(
                    "Vous ne pouvez passer que par la livraison manuelle"
                    " dans un devis, pas une commande confirmée"
                )
            )


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        # Overload to set carrier_id from the manual delivery wizard
        res = super()._get_new_picking_values()
        manual_delivery = self.env.context.get("bmg_stock")
        if manual_delivery:
            if manual_delivery.partner_id:
                res["partner_id"] = manual_delivery.partner_id.id
            if manual_delivery.carrier_id:
                res["carrier_id"] = manual_delivery.carrier_id.id
        return res

    def _search_picking_for_assignation(self):
        # Overload to filter carrier_id
        manual_delivery = self.env.context.get("bmg_stock")
        if manual_delivery:
            # original domain used in super()
            domain = [
                ("group_id", "=", self.group_id.id),
                ("location_id", "=", self.location_id.id),
                ("location_dest_id", "=", self.location_dest_id.id),
                ("picking_type_id", "=", self.picking_type_id.id),
                ("printed", "=", False),
                ("immediate_transfer", "=", False),
                (
                    "state",
                    "in",
                    [
                        "draft",
                        "confirmed",
                        "waiting",
                        "partially_available",
                        "assigned",
                    ],
                ),
            ]
            # Filter on carrier
            if manual_delivery.carrier_id:
                domain += [
                    ("carrier_id", "=", manual_delivery.carrier_id.id),
                ]
            return self.env["stock.picking"].search(domain, limit=1)
        else:
            return super()._search_picking_for_assignation()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_procured = fields.Float(
        string="Qté Livrée",
        help="Quantité déjà planifiée ou expédiée (mouvements de stock déjà créés)",
        compute="_compute_qty_procured",
        readonly=True,
        store=True,
    )
    qty_to_procure = fields.Float(
        string="A Livrer",
        help="Quantité en attente à ajouter à une livraison",
        compute="_compute_qty_to_procure",
        store=True,
        readonly=True,
    )

    @api.depends(
        "move_ids.state",
        "move_ids.scrapped",
        "move_ids.product_uom_qty",
        "move_ids.product_uom",
        "move_ids.location_id",
        "move_ids.location_dest_id",
    )
    def _compute_qty_procured(self):
        """
        Computes the already planned quantities for the given sale order lines,
        based on the existing stock.moves
        """
        for line in self:
            if line.qty_delivered_method == "stock_move":
                line.qty_procured = line._get_qty_procurement(
                    previous_product_uom_qty=False
                )

    @api.depends("product_uom_qty", "qty_procured")
    def _compute_qty_to_procure(self):
        """ Computes the remaining quantity to plan on sale order lines """
        for line in self:
            line.qty_to_procure = line.product_uom_qty - line.qty_procured

    def _get_procurement_group(self):
        # Overload to get the procurement.group for the right date / partner
        manual_delivery = self.env.context.get("bmg_stock")
        if manual_delivery:
            domain = [
                ("sale_id", "=", self.order_id.id),
                ("partner_id", "=", manual_delivery.partner_id.id),
            ]
            if manual_delivery.date_planned:
                domain += [
                    ("date_planned", "=", manual_delivery.date_planned),
                ]
            return self.env["procurement.group"].search(domain, limit=1)
        else:
            return super()._get_procurement_group()

    def _prepare_procurement_group_vals(self):
        # Overload to add manual.delivery fields to procurement.group
        res = super()._prepare_procurement_group_vals()
        manual_delivery = self.env.context.get("bmg_stock")
        if manual_delivery:
            res["partner_id"] = manual_delivery.partner_id.id
            res["date_planned"] = manual_delivery.date_planned
        return res

    def _prepare_procurement_values(self, group_id=False):
        # Overload to handle manual delivery date planned and route
        # This method ultimately prepares stock.move vals as its result is sent
        # to StockRule._get_stock_move_values.
        res = super()._prepare_procurement_values(group_id=group_id)
        manual_delivery = self.env.context.get("bmg_stock")
        if manual_delivery:
            if manual_delivery.date_planned:
                res["date_planned"] = manual_delivery.date_planned
            if manual_delivery.route_id:
                # `_get_stock_move_values` expects a recordset
                res["route_ids"] = manual_delivery.route_id
        return res

    def _action_launch_stock_rule_manual(self, previous_product_uom_qty=False):
        manual_delivery = self.env.context.get("bmg_stock")
        procurements = []
        for line in self:
            if line.state != "sale" or line.product_id.type not in ("consu", "product"):
                continue
            # Qty comes from the manual delivery wizard
            # This is different than the original method
            manual_line = manual_delivery.line_ids.filtered(
                lambda l: l.order_line_id == line
            )
            if not manual_line.quantity:
                continue
            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env["procurement.group"].create(
                    line._prepare_procurement_group_vals()
                )
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                # This part is different than the original method
                if group_id.move_type != line.order_id.picking_policy:
                    group_id.write({"move_type": line.order_id.picking_policy})
            values = line._prepare_procurement_values(group_id=group_id)
            line_uom = line.product_uom
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(
                manual_line.quantity, quant_uom
            )
            procurements.append(
                self.env["procurement.group"].Procurement(
                    line.product_id,
                    product_qty,
                    procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name,
                    line.order_id.name,
                    line.order_id.company_id,
                    values,
                )
            )
        if procurements:
            self.env["procurement.group"].run(procurements)
        return True

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        # Overload to skip launching stock rules on manual delivery lines
        # We only launch them when this is called from the manual delivery wizard
        manual_delivery_lines = self.filtered("order_id.manual_delivery")
        lines_to_launch = self - manual_delivery_lines
        return super(SaleOrderLine, lines_to_launch)._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
