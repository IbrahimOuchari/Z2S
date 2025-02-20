from odoo import models, fields, api, _, exceptions
import logging
from datetime import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ReturnComponentsWizard(models.TransientModel):
    _name = 'return.components.wizard'
    _description = 'Assistant de Retour de Composants'

    mrp_production_id = fields.Many2one('mrp.production', string="OF", required=True)
    line_ids = fields.One2many('return.components.line.wizard', 'wizard_id', string='Lignes')
    quantity_left = fields.Float(string='Quantity Left', compute='_compute_quantity_left', store=True, readonly=True)
    state = fields.Selection([
        ('non_solde', 'Non Soldé'),
        ('solde', 'Soldé')
    ], string='État', default='non_solde')




    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking')

    @api.model
    def default_get(self, fields):
        res = super(ReturnComponentsWizard, self).default_get(fields)
        production_id = self._context.get('default_mrp_production_id')

        if production_id:
            res['mrp_production_id'] = production_id
            production = self.env['mrp.production'].browse(res['mrp_production_id'])

            if production:
                lines_to_return = []
                for move in production.move_raw_ids:
                    if move.product_uom_qty > move.quantity_done:
                        quantity_left = move.product_uom_qty - move.quantity_done
                        stock_moves = self.env['stock.move'].search([
                            ('product_id', '=', move.product_id.id),
                            ('picking_id.origin', '=', production.name),
                            ('picking_id.state', '=', 'done')
                        ])
                        total_returned = sum(stock_moves.mapped('product_uom_qty'))
                        quantity_left -= total_returned

                        if quantity_left > 0:
                            lines_to_return.append((0, 0, {
                                'product_id': move.product_id.id,
                                'quantity': quantity_left,
                                'quantity_left': quantity_left,
                                'move_id': move.id
                            }))

                res['line_ids'] = lines_to_return
                res['state'] = 'non_solde'

        return res

    @api.onchange('stock_picking_id')
    def _onchange_stock_picking_id(self):
        """Track the state of the stock.picking."""
        if self.stock_picking_id and self.stock_picking_id.state == 'done':
            # Call default_get to refresh the wizard
            self.default_get(self.env.context.get('fields', []))
            _logger.info("Stock picking state is done. Default get called to refresh the wizard.")

    @api.onchange('move_raw_ids.quantity_left')
    def track_quantity_left(self):
        print("track quantity left ")
        quantity_left = self.quantity_left
        if quantity_left:
            print("ftech")
            self.default_get()

    def confirm(self):
        stock_picking = self.create_stock_picking()

        if stock_picking:
            self.stock_picking_id = stock_picking.id  # This will trigger the onchange
            self.create_stock_moves(stock_picking)
            self.update_stock_moves_quantity_left()

            # Further logic...

    def check_all_returned(self):
        """
        Check if all components have been returned.
        """
        all_zero = all(line.quantity_left == 0 for line in self.line_ids)

        if all_zero:
            _logger.info(_("Tous les composants ont été retournés pour la production %s") % self.mrp_production_id.name)
        else:
            _logger.info(_("Il reste des composants à retourner pour la production %s") % self.mrp_production_id.name)

    def create_stock_moves(self, stock_picking):
        if not stock_picking:
            _logger.error(_("Aucun picking de stock fourni."))
            return

        for line in self.line_ids:
            if line.quantity > 0:
                self.env['stock.move'].create({
                    'name': _('Retour de %s vers le stock') % line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'quantity_left': line.quantity - line.quantity_left,
                    'product_uom': line.product_id.uom_id.id,
                    'location_id': stock_picking.location_id.id,
                    'location_dest_id': stock_picking.location_dest_id.id,
                    'picking_id': stock_picking.id,
                })

        _logger.info(
            _("Ajouté %d mouvements de stock au picking de stock ID : %d") % (len(self.line_ids), stock_picking.id))

    def create_stock_picking(self):
        picking_type = self.env['stock.picking.type'].search([('sequence_code', '=', 'RT')], limit=1)
        if not picking_type:
            _logger.error(
                _("Type de picking de stock avec le code 'RT' non trouvé. Veuillez vérifier la configuration."))
            return False

        src_location = self.env['stock.location'].search([('usage', '=', 'production')], limit=1)
        dest_location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)

        if not src_location or not dest_location:
            _logger.error(_("Source ou destination de localisation non trouvée. Veuillez vérifier les emplacements."))
            return False

        sequence_name = self.generate_stock_picking_sequence()
        stock_picking = self.env['stock.picking'].create({
            'name': sequence_name,
            'picking_type_id': picking_type.id,
            'location_id': src_location.id,
            'location_dest_id': dest_location.id,
            'date_done': fields.Datetime.now(),
            'origin': self.mrp_production_id.name,
            'state': 'draft',
        })

        _logger.info(_("Créé le picking de stock avec ID : %d et nom : %s") % (stock_picking.id, sequence_name))
        return stock_picking

    def generate_stock_picking_sequence(self):
        current_year = datetime.now().strftime('%y')
        last_sequence = self.env['stock.picking'].search([('name', 'ilike', f'RT-{current_year}%')], order='name desc',
                                                         limit=1)

        if last_sequence:
            last_number = int(last_sequence.name.split('-')[-1])
        else:
            last_number = 0

        next_number = last_number + 1
        sequence_number = str(next_number).zfill(4)
        return f"RT-{current_year}-{sequence_number}"

    def update_stock_moves_quantity_left(self):
        for line in self.line_ids:
            if line.move_id:
                line.move_id.update_quantity_left()  # This will trigger the compute method in stock.move

        self.check_all_returned()  # After updating, check if all stock moves' quantity_left are zero

    #
    def action_mark_all_returned(self):
        for wizard in self:
            if wizard.mrp_production_id:
                wizard.mrp_production_id.write({'state_of': 'all_returned'})
                _logger.info('Production %s has been marked as all returned.', wizard.mrp_production_id.name)
            else:
                raise UserError(_('Production order not found.'))

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'The state has been updated to "All Returned".',
                'type': 'success'
            }
        }

    def action_print_results(self):
        # Method to print the results to the console
        for line in self.line_ids:
            _logger.info('Product: %s, Quantity Left: %s, Quantity Left Zero: %s',
                         line.product_id.display_name, line.quantity_left, line.quantity_left_zero)

    is_returned = fields.Boolean(string="Retourné", store=True)

    @api.onchange('line_ids.quantity_left')
    def _onchange_quantity(self):
        for line in self.line_ids:
            if line.quantity_left == 0:
                self.is_returned = True

    return_count = fields.Integer(string='Return Count', default=0)  # Track the return count

    @api.onchange('return_count')
    def _onchange_return_count(self):
        if self.mrp_production_id:
            self.mrp_production_id.return_count = self.return_count

    @api.onchange('mrp_production_id')
    def _onchange_mrp_production_id(self):
        if self.mrp_production_id:
            self.return_count = self.mrp_production_id.return_count




class ReturnComponentsWizardLine(models.TransientModel):
    _name = 'return.components.line.wizard'
    _description = 'Ligne de l\'Assistant de Retour de Composants'

    wizard_id = fields.Many2one('return.components.wizard', string='Référence de l\'Assistant')
    product_id = fields.Many2one('product.product', string='Produit')
    quantity = fields.Float(string='Quantité à Retourner', default=0.0)
    quantity_left = fields.Float(string='Quantité Restante', compute='_compute_quantity_left', store=True)
    move_id = fields.Many2one('stock.move', string='Mouvement de Stock')
    quantity_left_zero = fields.Boolean(string='Quantity Left Zero', default=False)

    @api.depends('quantity')
    def _compute_quantity_left(self):
        for line in self:
            if line.move_id:
                initial_quantity = line.move_id.product_uom_qty
                returned_quantity = sum(self.env['stock.move'].search([
                    ('product_id', '=', line.product_id.id),
                    ('picking_id', '=', line.move_id.picking_id.id),
                    ('state', '=', 'done')
                ]).mapped('product_uom_qty'))

                line.quantity_left = initial_quantity - returned_quantity - line.quantity
                _logger.debug('Product: %s, Quantity Left: %s', line.product_id.display_name, line.quantity_left)

                # Trigger compute_and_check_quantity_left in mrp.production
                if line.wizard_id and line.wizard_id.mrp_production_id:
                    production = line.wizard_id.mrp_production_id
                    _logger.info('Triggering compute_and_check_quantity_left for production %s', production.name)
                    production.compute_and_check_quantity_left()

    @api.onchange('quantity_left')
    def _onchange_quantity_left(self):
        """ Trigger the default_get logic when quantity_left changes. """
        if self.wizard_id:
            wizard = self.wizard_id
            wizard._update_line_ids()  # Custom method to refresh line_ids

    @api.onchange('quantity')
    def _onchange_quantity(self):
        """ Trigger action when 'quantity' changes and check if all quantities are zero. """
        if self.quantity_left == 0:
            self._check_and_update_all_returned()

    def _check_and_update_all_returned(self):
        """ Check if all components have been returned and update the production state. """
        if self.wizard_id:
            wizard = self.wizard_id
            all_lines = wizard.line_ids
            all_zero = all(line.quantity_left == 0 for line in all_lines)

            if all_zero:
                _logger.info(
                    _("Tous les composants ont été retournés pour la production %s") % wizard.mrp_production_id.name)
            else:
                _logger.info(
                    _("Il reste des composants à retourner pour la production %s") % wizard.mrp_production_id.name)

# In your ReturnComponentsWizard class, make sure to have the _update_line_ids method as defined earlier.
