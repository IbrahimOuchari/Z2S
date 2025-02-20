from odoo import api, fields, models, tools
from odoo import _


class MrpRouting(models.Model):
    _name = 'mrp.routing'
    _description = 'Routings'

    name = fields.Char('Routing', required=True)
    code = fields.Char(
        'Reference',
        copy=False, default=lambda self: _('New'), readonly=True)

    # Sequence pour gamme
    @api.model
    def create(self, vals):
        if 'code' not in vals or vals['code'] == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('mrp.routing') or _('New')
        return super(MrpRouting, self).create(vals)

    # Archiver Gamme
    active = fields.Boolean(default=True, string='Actif')

    def archive_record(self, record_id):
        record_to_archive = self.env['mrp.routing'].browse(record_id)
        if record_to_archive:
            record_to_archive.write({'active': False})
            return True
        return False

    note = fields.Text('Description')

    gamme_id = fields.One2many(
        'mrp.routing.operation', 'routing_id', 'Operations',
        copy=True)


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    routing_id = fields.Many2one(
        'mrp.routing', 'Parent Routing',
        index=True, required=True)
    gamme_name = fields.Char('mrp.routing')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    routing_id = fields.Many2one(
        'mrp.routing', 'Gamme',
        index=True, required=True)

    # operation_ids_1 = fields.One2many('mrp.routing', 'routing_id', 'Operations 1',
    #   copy=True)

    gamme_id = fields.One2many(
        'mrp.routing.operation', 'routing_id', 'Operations',
        copy=True)

    routing_id_id = fields.Many2one('mrp.routing.workcenter', related="routing_id")

    @api.onchange('routing_id')
    def create_one2many_record(self):
        if self.routing_id:
            self.operation_ids = [(0, 0, {
                'routing_id': line.routing_id,
                'name': line.name,
                'workcenter_id': line.workcenter_id,
                'time_cycle': line.time_cycle,
                'time_cycle_manual': line.time_cycle_manual,

            }) for line in self.routing_id.gamme_id]
            return


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        related='bom_id.routing_id', store=True, readonly=False, )

    operation_routing_id = fields.Many2one(
        'mrp.routing.workcenter', 'Consumed in Operation', check_company=True,
        domain="[('routing_id', '=', routing_id)]",
    )
