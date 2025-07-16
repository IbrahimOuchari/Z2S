from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MaintenanceOperationList(models.Model):
    _name = 'maintenance.operation.list'
    _description = 'Opérations par équipement'

    name = fields.Char("Nom de l'opération", required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')

    is_mensuelle = fields.Boolean(string="Mensuelle", store=True)
    is_trimestrielle = fields.Boolean(string="Trimestrielle", store=True)
    is_semestrielle = fields.Boolean(string="Semestrielle", store=True)
    is_annuelle = fields.Boolean(string="Annuelle", store=True)

    @api.constrains('is_mensuelle', 'is_trimestrielle', 'is_semestrielle', 'is_annuelle')
    def _check_at_least_one_frequency(self):
        for record in self:
            if not (record.is_mensuelle or record.is_trimestrielle or record.is_semestrielle or record.is_annuelle):
                raise ValidationError(
                    "Au moins un champ de fréquence doit être sélectionné (Mensuelle, Trimestrielle, Semestrielle ou Annuelle).")


class MaintenanceInterventionLine1(models.Model):
    _name = 'maintenance.intervention.line1'
    _description = 'Lignes d\'intervention maintenance'

    sequence = fields.Char(string="sequence")
    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.list', string="Opération")

    # Boolean frequency fields
    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    operation_name = fields.Char("Nom de l'opération", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1


class MaintenanceInterventionLine2(models.Model):
    _name = 'maintenance.intervention.line2'
    _description = 'Lignes d\'intervention maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.list', string="Opération")

    # Boolean frequency fields
    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    operation_name = fields.Char("Nom de l'opération", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1


class MaintenanceInterventionLine3(models.Model):
    _name = 'maintenance.intervention.line3'
    _description = 'Lignes d\'intervention maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.list', string="Opération")

    # Boolean frequency fields
    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    operation_name = fields.Char("Nom de l'opération", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1


class MaintenanceInterventionLine4(models.Model):
    _name = 'maintenance.intervention.line4'
    _description = 'Lignes d\'intervention maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.list', string="Opération")

    # Boolean frequency fields
    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    operation_name = fields.Char("Nom de l'opération", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1


class MaintenanceInterventionLine(models.Model):
    _name = 'maintenance.intervention.line'
    _description = 'Lignes d\'intervention maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.list', string="Opération", required=True)

    # Boolean frequency fields
    is_mensuelle = fields.Boolean(string="Mensuelle")
    is_trimestrielle = fields.Boolean(string="Trimestrielle")
    is_semestrielle = fields.Boolean(string="Semestrielle")
    is_annuelle = fields.Boolean(string="Annuelle")

    operation_name = fields.Char("Nom de l'opération", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1
