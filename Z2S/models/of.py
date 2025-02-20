from odoo import api, fields, models
from datetime import date
from odoo.tools import float_compare
from odoo.tools import float_is_zero
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class livraison_OF(models.Model):
    _inherit = 'mrp.production'

    date_creation = fields.Date(string="Date Création OF", default=lambda self: date.today())
    date_realisation = fields.Date(string="Date Réalisation",compute='_compute_today_date', store=True,)
    date_prevue_fin_prod = fields.Date(string="Date Prévue Fin Prod")

    def action_annule_of(self):
        for rec in self:
            rec.state = 'cancel'
            rec.state_of = 'cancel'

    @api.depends('state')
    def _compute_today_date(self):
        for record in self:
            if record.state == 'done':
                record.date_realisation = date.today()

    client_id = fields.Many2one('res.partner', string="Client", related="product_id.client_id")
    ref_product_client = fields.Char('product.template', related="product_id.ref_product_client")
    description = fields.Text('product.template', related="product_id.description_sale")

    stock_move_line_ids = fields.One2many('stock.move.line', 'ref_of', string='Liste des livraison sur l\'of')

    quantite_livre = fields.Float("Quantité Totale livrée", compute="_compute_qte", digits='Product Unit of Measure',
                                  index=True, store=True)
    quantity_done = fields.Integer('stock_move_line_ids.qty_done')
    quantite_restante = fields.Float("Quantité Reste à livrer", compute="_compute_qte_restante",
                                     digits='Product Unit of Measure', index=True, store=True)
    cout_of = fields.Float("Coût OF", compute="_compute_cout_of", digits='Product Price')

    @api.depends('move_raw_ids')
    def _compute_cout_of(self):
        for record in self:
            total = 0
            for rec in record.move_raw_ids:
                total += rec.cout_produit
            record.cout_of = total

    @api.depends('stock_move_line_ids', 'quantity_done', 'quantite_livre')
    def _compute_qte(self):
        for record in self:
            total = 0
            for rec in record.stock_move_line_ids:
                if rec.ref_of.name == record.name:
                    total += rec.qty_done
            record.quantite_livre = total

    @api.depends('qty_producing', 'quantite_livre', 'quantite_restante')
    def _compute_qte_restante(self):
        for record in self:
            reste = record.qty_producing - record.quantite_livre
            record.quantite_restante = reste

    active_livraison = fields.Boolean(default=False, string="Livraison Complète",
                                      store=True, compute="_compute_livraison_total")

    @api.depends('stock_move_line_ids', 'quantite_restante', 'qty_producing', 'quantite_livre')
    def _compute_livraison_total(self):
        for compute in self:
            if compute.quantite_restante == 0 and compute.qty_producing != 0:
                compute.active_livraison = True
            else:
                compute.active_livraison = False

    state_of = fields.Selection([
        ('none', 'Non Livré'),
        ('livre', 'Livré'),
        ('cancel', 'Annulé'),
    ], string='State OF',
        compute='_compute_state_mrp', copy=False, index=True, readonly=True, store=True,
        tracking=True)

    @api.depends('active_livraison', 'quantity_done', 'quantite_livre', 'quantite_restante', 'qty_producing')
    def _compute_state_mrp(self):
        for production in self:
            if production.quantite_restante == 0 and production.qty_producing != 0:
                production.state_of = 'livre'
            else:
                production.state_of = 'none'

    # Relation entre OF et BC

    num_bc = fields.Many2one('sale.order', string="N° BC Interne",
                             domain="[('state', '=', 'sale'), ('order_line.product_id', '=', product_id)]")

    num_bc_client = fields.Char(string="N° BC Client", related="num_bc.ref_client")

    # Tableau des opérations OF

    details_operation = fields.One2many('mrp.operation.of', 'production_id', string="Opérations")

    class StockPickingline(models.Model):
        _inherit = "stock.move"

        date_done_id = fields.Datetime(related="picking_id.date_done")
        num_bl = fields.Char(related="picking_id.name")
        cout_produit = fields.Float(related="product_id.last_purchase_price", string="Coût", digits='Product Price')

    # Tableau des opérations OF

    class MrpWorkorder(models.Model):
        _name = 'mrp.operation.of'

        name = fields.Text(string='Description', index=True, )
        production_id = fields.Many2one('mrp.production', 'Work Order', required=True, ondelete='cascade', index=True,
                                        copy=False)
        bom_id = fields.Many2one(related="production_id.bom_id", string="Nomenclature")
        gamme_id = fields.Many2one(related="bom_id.routing_id", string="Gamme")
        operation = fields.Many2one("mrp.routing.operation", string="Opération",
                                    domain="[('routing_id', '=', gamme_id)]")
        heure_debut = fields.Datetime(string="Heure Début")
        heure_fin = fields.Datetime(string="Heure Fin")
        duree = fields.Float(string="Durée", compute="_duree_operation")
        quantite = fields.Float(string="Quantité Produite")
        employee = fields.Many2one("hr.employee", string="Nom de Employée")

        @api.depends('heure_debut', 'heure_fin')
        def _duree_operation(self):
            for record in self:
                if record.heure_debut and record.heure_fin:
                    delta = record.heure_fin - record.heure_debut
                    record.duree = delta.total_seconds() / 3600  # Convertit la durée en heures
                else:
                    record.duree = 0.0

        @api.constrains('quantite', 'production_id')
        def check_quantite(self):
            for record in self:
                if record.quantite > record.production_id.product_qty:
                    raise ValidationError(
                        "La quantité produite ne peut pas être supérieure à la quantité de l'ordre de production.")
