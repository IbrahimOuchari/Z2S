from odoo import fields, models, api, exceptions

class HrZ2S(models.Model):
    _inherit = "hr.employee"
    _description = "Hr Num CNSS"

    num_cnss = fields.Char(string="N° CNSS")
    cin = fields.Char(string="N° CIN")
    delivred = fields.Date('Délivrez-le', store=True)
    bank_id = fields.Many2one('res.bank', string='Banque')
    affectation_id = fields.Many2one('hr.affectation', string='Affectation')

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    other_info = fields.Html()

    def _compute_attached_docs_count(self):
        attachment = self.env['ir.attachment']
        for emp in self:
            emp.doc_count = attachment.search_count([
                '&',
                ('res_model', '=', 'hr.employee'), ('res_id', '=', emp.id),
            ])

    def attachment_tree_view(self):
        attachment_action = self.env.ref('base.action_attachment')
        action = attachment_action.read()[0]
        action['domain'] = str([
            '&',
            ('res_model', '=', 'hr.employee'),
            ('res_id', 'in', self.ids),

        ])
        action['context'] = "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        return action

    sequence = fields.Char(string="Matricule", readonly=False, required=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'hr.employee.mat') or 'New'
        result = super(HrZ2S, self).create(vals)
        return result


class Affectation(models.Model):
    _name = "hr.affectation"
    _description = "Affectationa"
    _inherit = ['mail.thread']

    name = fields.Char('Nom', store=True, required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         "Le nom de l'affectation doit être unique!"),
    ]

    @api.model
    def create(self, values):
        """ We don't want the current user to be follower of all created Affectation """
        return super(Affectation, self.with_context(mail_create_nosubscribe=True)).create(values)
