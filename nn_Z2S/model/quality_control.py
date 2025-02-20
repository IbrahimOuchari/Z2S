from odoo import models, fields, api, exceptions, _


class QualityControl(models.Model):
    _name = 'control.quality'
    _description = 'Contrôle de Qualité'

    reference = fields.Char(
        string='Référence Fiche Contrôle',
        required=True,
        readonly=True,
        default=lambda self: _('Nouveau')
    )

    of_id = fields.Many2one(
        'mrp.production',
        string='Ordre de Fabrication',
        ondelete='set null',
        domain=[('state', 'in', ['done', 'progress'])]  # Show MRP productions in 'done' or 'in_progress' states
    )

    article_id = fields.Many2one('product.product', string='Article')
    client_reference = fields.Char(string='Référence Client')
    client_id = fields.Many2one('res.partner', string='Client')

    designation = fields.Char(string='Désignation')  # New field for designation
    qty_producing = fields.Float(string='Quantité Produite')  # New field for quantity produced

    type_1 = fields.Boolean(string='Type 1', default=False)
    type_2 = fields.Boolean(string='Type 2', default=False)
    type_3 = fields.Boolean(string='Type 3', default=False)

    type1_line_ids = fields.One2many('control.quality.type1.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type1')
    type2_line_ids = fields.One2many('control.quality.type2.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type2')
    type3_line_ids = fields.One2many('control.quality.type3.line', 'quality_id',
                                     string='Lignes de Contrôle Qualité De Type3')

    type1_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type1',
                                         store=True)
    type1_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type1',
                                             store=True)

    type2_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type2',
                                         store=True)
    type2_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type2',
                                             store=True)

    type3_conform_count = fields.Integer(string='Nombre Conforme', compute='_compute_conform_non_conform_type3',
                                         store=True)
    type3_non_conform_count = fields.Integer(string='Nombre Non Conforme', compute='_compute_conform_non_conform_type3',
                                             store=True)

    total_conform_count = fields.Integer(string='Total Nombre Conforme', compute='_compute_total_conform_non_conform',
                                         store=True)
    total_non_conform_count = fields.Integer(string='Total Nombre Non Conforme',
                                             compute='_compute_total_conform_non_conform', store=True)

    # New state with "in_progress"
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string='Statut', default='draft')

    @api.onchange('total_lines')
    def state_change(self):
        for record in self:
            if record.total_lines > 0:
                record.state = 'in_progress'
            else:
                record.state = 'draft'

    total_lines = fields.Integer(string='Total Lignes', compute='_compute_total_lines', readonly=True)

    @api.depends('type1_line_ids', 'type2_line_ids', 'type3_line_ids')
    def _compute_total_lines(self):
        for record in self:
            total_lines = (
                    len(record.type1_line_ids) +
                    len(record.type2_line_ids) +
                    len(record.type3_line_ids)
            )
            record.total_lines = total_lines

    def action_validate(self):
        for record in self:
            # Check if total_lines exceeds qty_producing
            if record.total_lines > record.of_id.qty_producing:
                raise exceptions.ValidationError(
                    "Erreur de validation : le nombre de lignes dépasse la quantité produite."
                )
            else:
                # Set state to 'done' if validation passes
                record.state = 'done'

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.reference}"
            result.append((record.id, name))
        return result

    @api.model
    def create(self, vals):
        if vals.get('reference', '/') == '/':
            current_year = fields.Date.today().strftime('%y')
            sequence = self.env['ir.sequence'].next_by_code('control.quality') or '0001'
            vals['reference'] = f"CQ - {current_year} - {sequence}"
        return super(QualityControl, self).create(vals)

    @api.onchange('of_id')
    def _onchange_of_id(self):
        if self.of_id:
            self.article_id = self.of_id.product_id.id
            self.client_id = self.of_id.client_id.id
            self.client_reference = self.of_id.ref_product_client
            self.designation = self.of_id.product_id.name  # Fetching designation
            self.qty_producing = self.of_id.product_qty  # Fetching quantity producing
        else:
            self.article_id = False
            self.client_id = False
            self.client_reference = False
            self.designation = False  # Reset designation if of_id is cleared
            self.qty_producing = False  # Reset quantity producing if of_id is cleared

    @api.depends('type1_line_ids.result1')
    def _compute_conform_non_conform_type1(self):
        for record in self:
            conform_count = sum(1 for line in record.type1_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type1_line_ids if line.result1 == 'non_conform')
            record.type1_conform_count = conform_count
            record.type1_non_conform_count = non_conform_count

    @api.depends('type2_line_ids.result1')
    def _compute_conform_non_conform_type2(self):
        for record in self:
            conform_count = sum(1 for line in record.type2_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type2_line_ids if line.result1 == 'non_conform')
            record.type2_conform_count = conform_count
            record.type2_non_conform_count = non_conform_count

    @api.depends('type3_line_ids.result1')
    def _compute_conform_non_conform_type3(self):
        for record in self:
            conform_count = sum(1 for line in record.type3_line_ids if line.result1 == 'conform')
            non_conform_count = sum(1 for line in record.type3_line_ids if line.result1 == 'non_conform')
            record.type3_conform_count = conform_count
            record.type3_non_conform_count = non_conform_count

    @api.depends('type1_conform_count', 'type1_non_conform_count',
                 'type2_conform_count', 'type2_non_conform_count',
                 'type3_conform_count', 'type3_non_conform_count')
    def _compute_total_conform_non_conform(self):
        for record in self:
            record.total_conform_count = (
                    record.type1_conform_count +
                    record.type2_conform_count +
                    record.type3_conform_count
            )
            record.total_non_conform_count = (
                    record.type1_non_conform_count +
                    record.type2_non_conform_count +
                    record.type3_non_conform_count
            )


class QualityControlLine(models.Model):
    _name = 'control.quality.line'
    _description = 'Ligne de Contrôle Qualité'

    quality_id = fields.Many2one('control.quality', string='Contrôle Qualité', ondelete='cascade')
    serial_number = fields.Char(string='Numéro de Série', required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('passed', 'Passé'),
        ('failed', 'Échoué')
    ], string='État', required=True, default='pending')
