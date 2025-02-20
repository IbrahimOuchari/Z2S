from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _description = "Product Template"

    name = fields.Char('Name', index=True, required=True, translate=True)

    @api.constrains('name')
    def _check_unique_name(self):
        for record in self:
            existing_records = self.search([('name', '=', record.name), ('id', '!=', record.id)])
            if existing_records:
                raise ValidationError("Un article avec le même nom existe déjà.")

    fourni = fields.Boolean(string="Produit Fourni", default=False)
    produit_fini = fields.Boolean(string="Produit Fini", default=False)
    sale_ok = fields.Boolean('Can be Sold', default=False)
    purchase_ok = fields.Boolean('Can be Purchased', default=False)
    client_id = fields.Many2one('res.partner', string="Client", domain="[('is_customer','=',True)]", store=True, )
    ref_product_client = fields.Char(string="Référence Client")

    @api.constrains('ref_product_client')
    def _check_unique_ref(self):
        for record in self:
            if record.ref_product_client:  # Vérifier si le champ n'est pas vide
                existing_records = self.search(
                    [('ref_product_client', '=', record.ref_product_client), ('id', '!=', record.id)])
                if existing_records:
                    raise ValidationError("Un article avec la même référence existe déjà.")

    # Validation du produit
    user_id = fields.Many2one('res.users', required=True, readonly=True)

    state_product = fields.Selection([
        ('draft', 'Brouillon'),
        ('0', 'Non Validé'),
        ('2', 'En Cours de Vérification'),
        ('1', 'Validé'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    produit_annule = fields.Boolean('Produit Annulé')


    def action_confirm_product(self):
        for rec in self:
            rec.state_product = '1'

    def action_cancel_product(self):
        for rec in self:
            rec.produit_annule = True

        action = self.env.ref('Z2S.action_wizard_cancel_reason').read()[0]
        action['context'] = {
            'default_product_id': self.id,
        }
        return action

    def action_verif_product(self):
        for rec in self:
            rec.state_product = '2'

    def action_set_draft_product(self):
        for rec in self:
            rec.state_product = 'draft'

    motif_validation_produit = fields.Text(string="Raison de Refus Produit")



    # Masquer le bouton modifier selon state
    hide_edit = fields.Html(string='Hide Edit', sanitize=False, compute='_compute_hide', store=False)

    @api.depends('state_product')
    def _compute_hide(self):
        for record in self:
            if record.state_product != 'draft' and not self.env.user.has_group('Z2S.modif_bouton_product'):
                record.hide_edit = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit = False


