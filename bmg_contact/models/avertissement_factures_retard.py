
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    overdue_invoice_count = fields.Integer(
        compute="_compute_overdue_invoice_count_amount",
        string="# des Factures Impayées",
        compute_sudo=True,
    )
    # the currency_id field on res.partner =
    # partner.company_id.currency_id or self.env.company.cueency_id
    overdue_invoice_amount = fields.Monetary(
        compute="_compute_overdue_invoice_count_amount",
        string="Factures en Retard Résiduel",
        compute_sudo=True, digits='Product Price',
        help="Montant résiduel total de la facture en retard dans la devise de l'entreprise.",
    )

    def _compute_overdue_invoice_count_amount(self):
        for partner in self:
            company_id = partner.company_id.id or partner.env.company.id
            (
                count,
                amount_company_currency,
            ) = partner._prepare_overdue_invoice_count_amount(company_id)
            partner.overdue_invoice_count = count
            partner.overdue_invoice_amount = amount_company_currency

    def _prepare_overdue_invoice_count_amount(self, company_id):
        self.ensure_one()
        domain = self._prepare_overdue_invoice_domain(company_id)
        rg_res = self.env["account.move"].read_group(
            domain, ["amount_residual_signed"], []
        )
        count = 0
        overdue_invoice_amount = 0.0
        if rg_res:
            count = rg_res[0]["__count"]
            overdue_invoice_amount = rg_res[0]["amount_residual_signed"]
        return (count, overdue_invoice_amount)

    def _prepare_overdue_invoice_domain(self, company_id):
        # The use of commercial_partner_id is in this method
        self.ensure_one()
        today = fields.Date.context_today(self)
        if company_id is None:
            company_id = self.env.company.id
        domain = [
            ("move_type", "=", "out_invoice"),
            ("company_id", "=", company_id),
            ("commercial_partner_id", "=", self.commercial_partner_id.id),
            ("invoice_date_due", "<", today),
            ("state", "=", "posted"),
            ("payment_state", "in", ("not_paid", "partial")),
        ]
        return domain

    def _prepare_jump_to_overdue_invoices(self, company_id):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        action["domain"] = self._prepare_overdue_invoice_domain(company_id)
        action["context"] = {
            "journal_type": "sale",
            "move_type": "out_invoice",
            "default_move_type": "out_invoice",
            "default_partner_id": self.id,
        }
        return action

    def jump_to_overdue_invoices(self):
        self.ensure_one()
        company_id = self.company_id.id or self.env.company.id
        action = self._prepare_jump_to_overdue_invoices(company_id)
        return action
