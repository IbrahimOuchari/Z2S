from odoo import models, fields, api


class CurativeMaintenanceRequest(models.Model):
    _name = 'maintenance.curative'
    _description = "Fiche d'Intervention Curative"
    name = fields.Char(string="Fiche d'Intervention", readonly=True, copy=False, default=lambda self: 'Nouveau')

    # Phase 1 : Déclaration de la Demande
    demandeur_hr = fields.Many2one('hr.employee', string="Demandeur HR", required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", required=True)
    reference_interne = fields.Char(
        string="Référence Interne",
        related='equipment_id.reference_interne',
        store=True,
        readonly=True
    )
    reference_centre = fields.Char(string="Référence Centre", required=True)
    declaration_date = fields.Date(string="Date Déclaration", readonly=True)
    problem_description = fields.Text(string="Problem Description", required=True)
    date_effective = fields.Date(string="Date Effective", required=True)
    date_intervention_souhaitee = fields.Date(string="Date Intervention Souhaitée")

    # Phase 2 : Diagnostic & Planification
    nom_intervenant = fields.Char(string="Nom & Prénom de l'Intervenant")
    diagnostic_date = fields.Date(string="Date Diagnostic")
    heure_debut = fields.Datetime(string="Date et Heure de Début")
    heure_fin = fields.Datetime(string="Date et Heure de Fin")
    rapport_diagnostique = fields.Text(string="Rapport Diagnostique")
    type_intervention = fields.Selection([
        ('interne', 'Interne'),
        ('externe', 'Externe')
    ], string="Type d'Intervention")
    besoin = fields.Boolean(string="Besoin ?")
    besoin_description = fields.Text(string="Détails du Besoin")
    objet_intervention = fields.Text(string="Objet de l'Intervention")
    date_prevue = fields.Date(string="Date Prévue")

    # Phase 3 : Réalisation
    intervenant = fields.Char(string="Intervenant")
    realisation_date = fields.Date(string="Date Réalisation")
    constat = fields.Text(string="Constat")
    pieces_rechange_ids = fields.One2many('maintenance.curative.piece', 'maintenance_id', string="Pièces de Rechange")
    description_intervention = fields.Text(string="Description de l'Intervention")
    action_corrective = fields.Boolean(string="Action Corrective Nécessaire ?")
    action_corrective_description = fields.Text(string="Détails de l'Action Corrective")
    validation_responsable = fields.Selection([
        ('valide', 'Validé'),
        ('non_valide', 'Non Validé')
    ], string="Validation Responsable")
    raison_non_validation = fields.Text(string="Raison de Non-Validation")

    # Phase 4 : Efficacité
    intervention_efficace = fields.Boolean(string="Intervention Efficace ?")
    efficacy_date = fields.Date(string="Date Efficacité")
    intervention_commentaire = fields.Text(string="Commentaire")

    # Phase 5 : Clôture
    responsable_intervention = fields.Char(string="Responsable de l'Intervention", default="Bassem")
    cloture_date = fields.Datetime(string="Date et Heure de Clôture")

    # State field
    state = fields.Selection([
        ('declaration', 'Déclaration de la Demande'),
        ('diagnostic', 'Diagnostic & Planification'),
        ('realisation', 'Réalisation'),
        ('efficacy', 'Efficacité'),
        ('cloture', 'Clôture')
    ], string="État", default='declaration', tracking=True)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('maintenance.curative') or 'Nouveau'
        return super(CurativeMaintenanceRequest, self).create(vals)

    # Declaration Date auto change due to state
    @api.onchange('state')
    def _onchange_state_dates(self):
        for record in self:
            if record.state == 'declaration':
                record.declaration_date = fields.Date.today()
            elif record.state == 'diagnostic':
                record.diagnostic_date = fields.Date.today()
            elif record.state == 'realisation':
                record.realisation_date = fields.Date.today()
            elif record.state == 'efficacy':
                record.efficacy_date = fields.Date.today()
            elif record.state == 'cloture':
                record.cloture_date = fields.Datetime.now()

    # State changes Button Group
    def move_to_diagnostic(self):
        self.state = 'diagnostic'

    def move_to_realisation(self):
        self.state = 'realisation'

    def move_to_efficacy(self):
        self.state = 'efficacy'

    def move_to_cloture(self):
        self.state = 'cloture'


class MaintenanceCurativePiece(models.Model):
    _name = 'maintenance.curative.piece'
    _description = "Pièce de Rechange"

    maintenance_id = fields.Many2one('maintenance.curative', string="Fiche de Maintenance")
    reference_piece = fields.Char(string="Référence")
    piece_rechange = fields.Char(string="Pièce de Rechange")


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = "Équipement de Maintenance"

    reference_interne = fields.Char(string="Référence Interne", store=True)
