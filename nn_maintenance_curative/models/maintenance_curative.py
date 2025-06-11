from datetime import date, timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError


class CurativeMaintenanceRequest(models.Model):
    _name = 'maintenance.curative'
    _description = "Fiche d'Intervention Curative"
    name = fields.Char(string="Fiche d'Intervention", readonly=True, copy=False, default=lambda self: 'Nouveau')

    # Phase 1 : Déclaration de la Demande
    demandeur_hr = fields.Many2one('hr.employee', string="Demandeur HR", required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", required=True, store=True)
    reference_interne = fields.Char(
        string="Référence Interne",
        store=True,
        readonly=True
    )
    sn = fields.Char(string="SN", required=True)
    declaration_date = fields.Date(string="Date Déclaration", required=True, readonly=True)
    problem_description = fields.Text(string="Problem Description", required=True)
    date_effective = fields.Date(string="Date Effective", required=True)
    date_intervention_souhaitee = fields.Date(string="Date Intervention Souhaitée", required=True)
    color = fields.Integer(string='Couleur', compute='_compute_color')

    @api.depends('date_intervention_souhaitee')
    def _compute_color(self):
        for rec in self:
            if rec.date_intervention_souhaitee == date.today() + timedelta(days=1):
                rec.color = 1  # Red (index 1)
            else:
                rec.color = 0  # Default (grey)

    # Phase 2 : Diagnostic & Planification
    nom_intervenant = fields.Char(string="Nom & Prénom de l'Intervenant")
    existing_intervenant = fields.Boolean(string="Intervenant Existe")
    intervenant_hr = fields.Many2one('hr.employee', string="Nom & Prénom de l'Intervenant", )
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
    date_prevue = fields.Date(string="Date Prévue de l'intervention")

    # Phase 3 : Réalisation
    intervenant = fields.Char(string="Intervenant")
    existing_intervenant_realisation = fields.Boolean(string="Intervenant Existe")
    intervenant_hr_realisation = fields.Many2one('hr.employee', string="Nom & Prénom de l'Intervenant", )
    realisation_date = fields.Date(string="Date Réalisation")
    constat = fields.Text(string="Constaté")
    spare_part_ids = fields.One2many(
        'maintenance.curative.spare.part',
        'curative_id',
        string='Pièces de rechange'
    )
    spare_part_demand_ids = fields.One2many(
        'maintenance.curative.spare.part.demand',
        'curative_id',
        string='Pièces de rechange demandées'
    )

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
    intervention_commentaire = fields.Text(string="Nouvelle Fiche d'intervention")

    # Phase 5 : Clôture
    responsable_intervention = fields.Many2one(
        'res.users',
        string="Responsable de l'Intervention",
        default=lambda self: self.env['res.users'].search([('name', '=', 'Bassem Zouari')], limit=1).id
    )

    cloture_date = fields.Datetime(string="Date et Heure de Clôture")

    # State field
    state = fields.Selection([
        ('declaration', 'Déclaration de la Demande'),
        ('diagnostic', 'Diagnostic & Planification'),
        ('realisation', 'Réalisation'),
        ('efficacy', 'Efficacité'),
        ('cloture', 'Clôture')
    ], string="État", default='declaration', tracking=True)

    # Function on change or depends

    @api.onchange('date_effective')
    def _onchange_date_effective(self):
        today = fields.Date.today()
        if self.date_effective and self.date_effective < today:
            self.date_effective = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date effective ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    @api.onchange('diagnostic_date')
    def _onchange_diagnostic_date(self):
        today = fields.Date.today()
        if self.diagnostic_date and self.diagnostic_date < today:
            self.diagnostic_date = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date Diagnostic ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    @api.onchange('date_prevu')
    def _onchange_date_prevu(self):
        today = fields.Date.today()
        if self.date_prevu and self.date_prevu < today:
            self.date_prevu = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date prévu ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    @api.onchange('equipment_id')
    def _onchange_reference_interne(self):
        for record in self:
            if record.equipment_id and record.equipment_id.reference_interne:
                record.reference_interne = record.equipment_id.reference_interne
            else:
                record.reference_interne = False

    @api.onchange('heure_debut', 'heure_fin')
    def _onchange_date_heure_date_fin(self):
        for record in self:
            if record.heure_debut and record.heure_fin:
                if record.heure_debut >= record.heure_fin:
                    return {
                        'warning': {
                            'title': "Attention",
                            'message': "L'heure de début doit être inférieure à l'heure de fin."
                        }
                    }

    @api.onchange('realisation_date')
    def _onchange_realisation_date(self):
        today = fields.Date.today()
        if self.realisation_date and self.realisation_date < today:
            self.realisation_date = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date Réalisation ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    @api.onchange('efficacy_date')
    def _onchange_efficacy_date(self):
        today = fields.Date.today()
        if self.efficacy_date and self.efficacy_date < today:
            self.efficacy_date = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date Efficacité ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    @api.onchange('cloture_date')
    def _onchange_cloture_date(self):
        today = fields.Date.today()
        if self.cloture_date and self.cloture_date < today:
            self.cloture_date = today
            return {
                'warning': {
                    'title': "Date incorrecte",
                    'message': "La date Clôture ne peut pas être antérieure à aujourd'hui. Elle a été mise à jour automatiquement."
                }
            }

    # ===================================================================================================================

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
        for rec in self:
            new_lines = []
            for op in rec.spare_part_demand_ids:
                new_lines.append((0, 0, {
                    'product_id': op.product_id.id,
                    'quantity': op.quantity,
                    'curative_id': op.curative_id.id,
                }))
            rec.spare_part_ids = new_lines

    def move_to_efficacy(self):
        self.state = 'efficacy'

    def move_to_cloture(self):
        self.state = 'cloture'

    picking_id = fields.Many2one(
        'stock.picking',
        string="Bon de Livraison",
        copy=False
    )

    def action_create_stock_picking(self):
        for record in self:

            # Get Picking Type with code 'MT'
            picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'MT')], limit=1)
            if not picking_type:
                raise UserError("Aucun type d'opération de transfert interne avec code 'MT' n'a été trouvé.")

            # Create Stock Picking
            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'origin': record.name,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id
            })

            # Create stock.move lines
            for line in record.spare_part_ids:
                if not line.product_id or not line.quantity:
                    continue
                self.env['stock.move'].create({
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.product_variant_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': picking.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                })

            # Mark the record as created and store picking
            # Mark the record as created and link the picking
            record.stock_pick_created = True
            record.picking_id = picking.id

            # Return picking view
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.picking',
                'view_mode': 'form',
                'res_id': picking.id,
                'target': 'current',
            }
        return None

    stock_pick_created = fields.Boolean(string="Stock Picking Créé", default=False)

    def action_view_stock_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError("Aucun transfert associé.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfert',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': self.picking_id.id,
            'target': 'current',
        }


class MaintenanceCurativePiece(models.Model):
    _name = 'maintenance.curative.piece'
    _description = "Pièce de Rechange"

    maintenance_id = fields.Many2one('maintenance.curative', string="Fiche de Maintenance")
    reference_piece = fields.Char(string="Référence")
    piece_rechange = fields.Char(string="Pièce de Rechange")


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    _description = "Équipement de Maintenance"

    reference_interne = fields.Char(string="Référence Interne")
