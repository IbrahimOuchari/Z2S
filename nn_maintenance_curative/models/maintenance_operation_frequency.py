from odoo import models, fields, api


class MaintenanceOperationFrequente(models.Model):
    _name = 'maintenance.operation.frequente'
    _description = 'Opérations par fréquence'

    name = fields.Char("Nom de l'opération", required=True)
    frequency_name = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence associée", required=True)


class MaintenanceInterventionLine1(models.Model):
    _name = 'maintenance.intervention.line1'
    _description = 'Lignes d\'intervention maintenance'

    equipment_id = fields.Many2one('maintenance.equipment', string="Équipement", ondelete='cascade')
    numero = fields.Integer("N°", compute="_compute_numero", store=True)
    operation_id = fields.Many2one('maintenance.operation.frequente', string="Opération")
    frequency = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence", default='1')
    ""
    frequency_name = fields.Char("Nom de la fréquence", readonly=True)
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
    operation_id = fields.Many2one('maintenance.operation.frequente', string="Opération")
    frequency = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence", default='1')
    frequency_name = fields.Char("Nom de la fréquence", readonly=True)
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
    operation_id = fields.Many2one('maintenance.operation.frequente', string="Opération")
    frequency = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence", default='1')
    frequency_name = fields.Char("Nom de la fréquence", readonly=True)
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
    operation_id = fields.Many2one('maintenance.operation.frequente', string="Opération")
    frequency = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence", default='1')
    frequency_name = fields.Char("Nom de la fréquence", readonly=True)
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
    operation_id = fields.Many2one('maintenance.operation.frequente', string="Opération", required=True)
    frequency = fields.Selection([
        ('1', 'Fréquence 1'),
        ('2', 'Fréquence 2'),
        ('3', 'Fréquence 3'),
        ('4', 'Fréquence 4'),
    ], string="Fréquence", default='1')
    frequency_name = fields.Char("Nom de la fréquence", readonly=True)
    ok = fields.Boolean("OK ✅")
    nok = fields.Boolean("NOK ❌")
    observations = fields.Text("Observations")

    @api.depends('equipment_id')
    def _compute_numero(self):
        for idx, record in enumerate(
                sorted(self, key=lambda r: r.id if r.id else 0)):  # Sort by id, default to 0 for unsaved records
            record.numero = idx + 1
