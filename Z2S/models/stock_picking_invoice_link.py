from odoo import _, fields, models, api
from odoo.exceptions import UserError
from odoo.tools import float_compare

# Account move

class AccountMove(models.Model):
    _inherit = "account.move"

    picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Related Pickings",
        store=True,
        compute="_compute_picking_ids",
        help="Related pickings "
        "(only when the invoice has been generated from a sale order).",
    )


    @api.depends("invoice_line_ids", "invoice_line_ids.move_line_ids")
    def _compute_picking_ids(self):
        for invoice in self:
            invoice.picking_ids = invoice.mapped(
                "invoice_line_ids.move_line_ids.picking_id"
            )

    def action_show_picking(self):
        """This function returns an action that display existing pickings
        of given invoice.
        It can either be a in a list or in a form view, if there is only
        one picking to show.
        """
        self.ensure_one()
        form_view_name = "stock.view_picking_form"
        xmlid = "stock.action_picking_tree_all"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if len(self.picking_ids) > 1:
            action["domain"] = "[('id', 'in', %s)]" % self.picking_ids.ids
        else:
            form_view = self.env.ref(form_view_name)
            action["views"] = [(form_view.id, "form")]
            action["res_id"] = self.picking_ids.id
        return action


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_line_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_invoice_line_rel",
        column1="invoice_line_id",
        column2="move_id",
        string="Related Stock Moves",
        readonly=True,
        help="Related stock moves "
        "(only when the invoice has been generated from a sale order).",
    )

# Sale Order

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_stock_moves_link_invoice(self):
        return self.mapped("move_ids").filtered(
            lambda mv: (
                mv.state == "done"
                and not (
                    any(
                        inv.state != "cancel"
                        for inv in mv.invoice_line_ids.mapped("move_id")
                    )
                )
                and not mv.scrapped
                and (
                    mv.location_dest_id.usage == "customer"
                    or (mv.location_id.usage == "customer" and mv.to_refund)
                )
            )
        )

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        stock_moves = self.get_stock_moves_link_invoice()
        # Invoice returned moves marked as to_refund
        if (
            float_compare(
                self.qty_to_invoice, 0.0, precision_rounding=self.currency_id.rounding
            )
            < 0
        ):
            stock_moves = stock_moves.filtered(
                lambda m: m.to_refund and not m.invoice_line_ids
            )
        vals["move_line_ids"] = [(4, m.id) for m in stock_moves]
        return vals


# Stock move

class StockMove(models.Model):
    _inherit = "stock.move"

    invoice_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="stock_move_invoice_line_rel",
        column1="move_id",
        column2="invoice_line_id",
        string="Invoice Line",
        copy=False,
        readonly=True,
    )

    def write(self, vals):
        """
        User can update any picking in done state, but if this picking already
        invoiced the stock move done quantities can be different to invoice
        line quantities. So to avoid this inconsistency you can not update any
        stock move line in done state and have invoice lines linked.
        """
        if "product_uom_qty" in vals and not self.env.context.get(
            "bypass_stock_move_update_restriction"
        ):
            for move in self:
                if move.state == "done" and move.invoice_line_ids:
                    raise UserError(_("You can not modify an invoiced stock move"))
        return super().write(vals)

# Stock picking

class StockPicking(models.Model):
    _inherit = "stock.picking"

    invoice_ids = fields.Many2many(
        comodel_name="account.move", copy=False, string="Invoices", readonly=True
    )

    def action_view_invoice(self):
        """This function returns an action that display existing invoices
        of given stock pickings.
        It can either be a in a list or in a form view, if there is only
        one invoice to show.
        """
        self.ensure_one()
        form_view_name = "account.view_move_form"
        xmlid = "account.action_move_out_invoice_type"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        if len(self.invoice_ids) > 1:
            action["domain"] = "[('id', 'in', %s)]" % self.invoice_ids.ids
        else:
            form_view = self.env.ref(form_view_name)
            action["views"] = [(form_view.id, "form")]
            action["res_id"] = self.invoice_ids.id
        return action
