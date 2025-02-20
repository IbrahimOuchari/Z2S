from odoo import models, fields, api


class CrmStageSequence(models.Model):
    _inherit = "crm.stage"

    ordre = fields.Integer(string="Séquence")


class CrmStageChange(models.Model):
    _inherit = 'crm.lead'

    ordre_id = fields.Integer(string="Séquence", related="stage_id.ordre")
    next_ordre_id = fields.Integer(string="Séquence Suivante", compute="_compute_next_ordre_id")

    client = fields.Selection(
        [('0', 'Ancien Client'), ('1', 'Nouveau Client')], string="Prospect",
        required=True, default=False, index=True)

    def _compute_next_ordre_id(self):
        for ordre in self:
            ordre.next_ordre_id = ordre.ordre_id + 1

    def change_stage_with_next_ordre_id(self):
        for lead in self:
            next_stage = self.env['crm.stage'].search([('ordre', '=', lead.next_ordre_id)], limit=1)
            if next_stage:
                lead.stage_id = next_stage.id
                lead.create_stage_change_history()


class CrmStageChangeHistory(models.Model):
    _name = 'crm.stage.change.history'
    _description = 'Historique des changements de stage'

    lead_id = fields.Many2one('crm.lead', string="Opportunité")
    partner_id = fields.Many2one(related="lead_id.partner_id")
    stage_id = fields.Many2one('crm.stage', string="Statut")
    date_start = fields.Date(string="Date de début")
    date_end = fields.Date(string="Date de fin")

    @api.model
    def create(self, vals):
        # Auto-fill date_start on creation
        vals['date_start'] = fields.Datetime.now()
        return super(CrmStageChangeHistory, self).create(vals)

    def end_stage(self):
        for history in self:
            history.date_end = fields.Datetime.now()


class CrmStageChange(models.Model):
    _inherit = 'crm.lead'

    stage_change_history_ids = fields.One2many('crm.stage.change.history', 'lead_id',
                                               string="Historique des changements de stage")

    @api.model
    def create(self, values):
        new_lead = super(CrmStageChange, self).create(values)
        new_lead.create_stage_change_history()
        return new_lead

    def create_stage_change_history(self):
        history_obj = self.env['crm.stage.change.history']
        for lead in self:
            new_history_vals = {
                'lead_id': lead.id,
                'stage_id': lead.stage_id.id,
            }

            # Vérifier si l'historique est vide ou si le dernier enregistrement est terminé
            if not lead.stage_change_history_ids or lead.stage_change_history_ids[-1].date_end:
                new_history_vals['date_start'] = fields.Datetime.now()

            # Mettre fin à l'enregistrement précédent (s'il est en cours)
            if lead.stage_change_history_ids and not lead.stage_change_history_ids[-1].date_end:
                lead.stage_change_history_ids[-1].end_stage()

            new_history = history_obj.create(new_history_vals)
            lead.write({'stage_change_history_ids': [(4, new_history.id)]})

        return True
