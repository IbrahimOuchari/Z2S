from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    ref_product_client_manual = fields.Char(string="Reference Articles étiquette", required=True)

    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
            ('type', '=', 'normal'),
            ('state', '=', 'done')
        ]""",
        check_company=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product and sets BOM if state is 'done'."""
        _logger.info("onchange_product_id method called")
        if not self.product_id:
            self.bom_id = False
        else:
            picking_type_id = self._context.get('default_picking_type_id')
            picking_type = picking_type_id and self.env['stock.picking.type'].browse(picking_type_id)
            domain = [
                '|',
                    ('company_id', '=', False),
                    ('company_id', '=', self.company_id.id),
                '|',
                    ('product_id', '=', self.product_id.id),
                    '&',
                        ('product_tmpl_id.product_variant_ids', '=', self.product_id.id),
                        ('product_id', '=', False),
                ('type', '=', 'normal'),
                ('state', '=', 'done')
            ]
            _logger.info(f"Domain: {domain}")
            bom = self.env['mrp.bom'].search(domain, limit=1)
            if bom:
                self.bom_id = bom.id
                self.product_qty = bom.product_qty
                self.product_uom_id = bom.product_uom_id.id
            else:
                self.bom_id = False
                self.product_uom_id = self.product_id.uom_id.id