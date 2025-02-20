from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLeadProduct(models.Model):
    _name = 'crm.lead.product'

    product_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description')
    qty = fields.Float(string='Quantité', default=1.0, digits='Product Unit of Measure')
    product_uom = fields.Many2one('uom.uom', string='Unité de Mesure')
    price_unit = fields.Float(string='Prix Unitaire')
    tax_id = fields.Many2many('account.tax', string='T.V.A.')
    lead_id = fields.Many2one('crm.lead')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            self.price_unit = self.product_id.lst_price
            self.product_uom = self.product_id.uom_id.id
            self.tax_id = self.product_id.taxes_id.ids


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    lead_product_ids = fields.One2many('crm.lead.product', 'lead_id', string='Produits pour Devis')
    devis_ids = fields.One2many('sale.devis', 'opportunity_id', string='Devis')

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id', 'devis_ids.state', 'devis_ids.currency_id', 'devis_ids.amount_untaxed',
                 'devis_ids.date_devis', 'devis_ids.company_id')
    def _compute_sale_data(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for devis in lead.devis_ids:
                if devis.state in ('devis', 'confirme'):
                    quotation_cnt += 1
            for order in lead.order_ids:
                if order.state in ('sale', 'fait'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.quotation_count = quotation_cnt
            lead.sale_order_count = sale_order_cnt

    def action_create_quotation(self):
        devis_lines = []
        for line in self.lead_product_ids:
            devis_lines.append((0, 0, {'product_id': line.product_id.id,
                                       'name': line.description,
                                       'qty': line.qty,
                                       'product_uom': line.product_uom.id,
                                       'price_unit': line.price_unit,
                                       'tax_id': [(6, 0, line.tax_id.ids)]
                                       }))

        if self.partner_id:
            vals = ({
                'default_partner_id': self.partner_id.id,
                'default_team_id': self.team_id.id,
                'default_campaign_id': self.campaign_id.id,
                'default_medium_id': self.medium_id.id,
                'default_source_id': self.source_id.id,
                'default_opportunity_id': self.id,
                'default_devis_line': devis_lines,
            })
        else:
            raise UserError('Afin de créer un devis client, le champ Client ne doit pas être vide!')

        return {
            'name': "Create Sale Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.devis',
            'target': 'current',
            'context': vals,
        }

    devis_ids = fields.One2many('sale.devis', 'opportunity_id', string='Devis')

    def action_view_sale_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("bmg_sale.devis_action")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id)]
        quotations = self.mapped('devis_ids')
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('bmg_sale.sale_devis_form_view').id, 'form')]
            action['res_id'] = quotations.id
        return action


class SaleDevis(models.Model):
    _inherit = 'sale.devis'

    opportunity_id = fields.Many2one('crm.lead', string='Produits pour Devis')

    def _prepare_sale_devis_lines_from_opportunity(self, record):
        data = {
            'product_id': record.product_id.id,
            'name': record.description,
            'qty': record.qty,
            'product_uom': record.product_uom.id,
            'price_unit': record.product_id.lst_price
        }
        return data

    @api.onchange('opportunity_id')
    def opportunity_id_change(self):
        if not self.opportunity_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.opportunity_id.partner_id.id

        new_lines = self.env['sale.devis.line']
        for line in self.opportunity_id.lead_product_ids:
            data = self._prepare_sale_devis_lines_from_opportunity(line)
            new_line = new_lines.new(data)
            new_lines += new_line

        self.devis_line += new_lines
        return {}
