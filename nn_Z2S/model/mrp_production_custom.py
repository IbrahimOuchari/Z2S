import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

# Configure logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    date_prevue_fin_prod = fields.Date(string="Date Prévue Fin Prod", required=True)

    quality_control_checked = fields.Boolean(
        string="Contrôle Qualité Vérifié",
        default=False,  # Default value set to False
        store=True  # Store the field value to persist it in the database
    )
    # Rename "Durée Attendue" to "Durée Théorique" and control editability
    duration_expected = fields.Float(
        string='Durée Théorique',
        readonly=True,  # Field is read-only by default
        states={'draft': [('readonly', True)]}  # Editable only in 'draft' state
    )

    total_duration_real = fields.Char(
        string='Durée Réelle Totale',
        compute='_compute_total_duration_real'
    )

    total_duration_theoretical = fields.Char(
        string='Durée Théorique Totale',
        compute='_compute_total_duration_theoretical'
    )
    # Field to store the productivity percentage
    productivity = fields.Float(
        string='Productivité (%)',
        compute='_compute_productivity',  # Compute productivity based on total durations
        digits=(16, 3)  # Compute productivity based on total durations
    )
    # New field to display productivity with a percentage sign
    productivity_display = fields.Char(
        string='Productivité',
        compute='_compute_productivity_display',  # New compute method for display
        store=False  # Not stored in the database
    )

    @api.depends('productivity')
    def _compute_productivity_display(self):
        for order in self:
            # Format the float productivity to a string with a percentage sign
            order.productivity_display = order.productivity

    label_management_ids = fields.One2many(
        'label.management',
        'manufacturing_order_id',
        string="Label Management",
        readonly=True
    )

    qty_producing_stored = fields.Float(
        string='Quantité de Production Stockée',
        readonly=True,
        compute='_compute_qty_producing_stored'
    )
    client_id = fields.Many2one('res.partner', string='Client')

    quantity_per_batch = fields.Float(string="Colisage", required=True, digits=(16, 0))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ Fetch the quantity per batch default from the product template when the product is changed """
        if self.product_id:
            # Accessing the product's template to fetch the default batch quantity
            self.quantity_per_batch = self.product_id.quantity_per_batch_default
        else:
            # Reset the value if no product is selected
            self.quantity_per_batch = 0.0

    @api.constrains('quantity_per_batch')
    def _check_quantity_per_batch(self):
        """ Ensure that the quantity per batch is not zero """
        for record in self:
            if record.quantity_per_batch == 0.0:
                raise ValidationError(
                    "La quantité par colisage ne peut pas être égale à zéro. Veuillez entrer une valeur valide.")

    is_readonly_lot = fields.Boolean(string="Readonly Lot", default=True)

    def unblock_lot(self):
        # Toggle the readonly status
        for record in self:
            record.is_readonly_lot = not record.is_readonly_lot

            # # You can also change the state of related label_management_ids here if needed
            # for label in record.label_management_ids:
            #     label.is_readonly_lot = not label.is_readonly_lot

    def block_lot(self):
        # Toggle the readonly status
        for record in self:
            record.is_readonly_lot = not record.is_readonly_lot
            # # You can also change the state of related label_management_ids here if needed
            # for label in record.label_management_ids:
            #     label.is_readonly_lot = not label.is_readonly_lot

    def get_label_management_data(self):
        """Method to fetch related label.management records"""
        label_records = self.env['label.management'].search([
            ('manufacturing_order_id', '=', self.id)
        ])
        return label_records

    def print_label_management_report(self):
        """Fetch related label management records and print the report."""
        label_records = self.env['label.management'].search([
            ('manufacturing_order_id', '=', self.id)
        ])
        if label_records:
            return self.env.ref('nn_z2s.action_label_management_report').report_action(label_records)
        else:
            raise ValueError("No Label Management records found for this Manufacturing Order.")

    @api.depends('workorder_ids.duration_expected')
    def _compute_total_duration_theoretical(self):
        for order in self:
            try:
                # Calculate the total theoretical duration (in minutes)
                total_theoretical_duration = sum(order.workorder_ids.mapped('duration_expected'))  # This is in minutes
                # Convert minutes to seconds for formatting
                total_seconds = total_theoretical_duration * 60  # Convert minutes to seconds
                formatted_string = self._format_duration(total_seconds)  # Format in H M S
                order.total_duration_theoretical = formatted_string
            except Exception as e:
                _logger.error(f"Erreur lors du calcul de la durée théorique totale pour la commande {order.id}: {e}")
                order.total_duration_theoretical = "Aucune Durée"

    @api.depends('workorder_ids.real_duration_float')
    def _compute_total_duration_real(self):
        for record in self:
            total_minutes = sum(record.workorder_ids.mapped('real_duration_float'))
            total_seconds = int(total_minutes * 60)

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            result = []
            if hours:
                result.append(f"{hours} H")
            if minutes:
                result.append(f"{minutes} M")
            if seconds or not result:  # Show 0 S if total is 0
                result.append(f"{seconds} S")

            record.total_duration_real = ' '.join(result)

    @api.depends('workorder_ids.productivity')
    def _compute_productivity(self):
        for rec in self:
            valid_prod = [wo.productivity for wo in rec.workorder_ids if wo.productivity > 0]
            rec.productivity = sum(valid_prod) / len(valid_prod) if valid_prod else 0.0

    def _extract_seconds_from_duration(self, duration_str):
        total_seconds = 0
        if not duration_str:
            return total_seconds

        try:
            parts = duration_str.split()
            for part in parts:
                if 'H' in part:  # Hours
                    hours = int(part.replace('H', '').strip())
                    total_seconds += hours * 3600
                elif 'M' in part:  # Minutes
                    minutes = int(part.replace('M', '').strip())
                    total_seconds += minutes * 60
                elif 'S' in part:  # Seconds
                    seconds = int(part.replace('S', '').strip())
                    total_seconds += seconds
        except Exception as e:
            _logger.error(f"Erreur lors de l'extraction des secondes de la durée '{duration_str}': {e}")

        return total_seconds

    def _format_duration(self, total_seconds):
        try:
            if total_seconds <= 0:
                return "Aucune Durée"

            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)

            parts = []
            if hours > 0:
                parts.append(f"{hours}H")
            if minutes > 0:
                parts.append(f"{minutes}M")
            if seconds > 0:
                parts.append(f"{seconds}S")

            return " ".join(parts) if parts else "Aucune Durée"
        except Exception as e:
            _logger.error(f"Erreur lors du formatage de la durée {total_seconds}: {e}")
            return "Aucune Durée"

    @api.depends('qty_producing')
    def _compute_qty_producing_stored(self):
        """
        Compute the stored quantity of production based on `qty_producing`.
        """
        for order in self:
            order.qty_producing_stored = order.qty_producing

    def action_create_lots(self):
        """
        Create lots for the manufacturing order based on the `qty_producing` value.
        """
        for order in self:
            qty_producing = order.qty_producing
            quantity_per_batch = order.quantity_per_batch

            if qty_producing <= 0:
                raise UserError("La quantité à produire doit être supérieure à zéro.")

            if quantity_per_batch <= 0:
                raise UserError("La quantité colisage doit être supérieure à zéro.")
            if quantity_per_batch > qty_producing:
                raise UserError("La quantité clisage ne peut pas être supérieure à la quantité à produire.")

            self.env['label.management'].create_lots_for_order(order, qty_producing)

    return_count = fields.Integer(string="Retour des Composants", compute="_compute_return_count")

    @api.depends('name')
    def _compute_return_count(self):
        for production in self:
            production.return_count = self.env['stock.picking'].search_count([
                ('origin', '=', production.name),
                ('picking_type_id.sequence_code', '=', 'RT'),
                ('state', '!=', 'done')  # Exclude 'done' return operations
            ])

    control_quality_done = fields.Integer(string="Controle Qualite done")

    @api.depends('name')
    def _compute_control_quality_done(self):
        for production in self:
            # Count the number of related control quality records that are in 'done' or 'in_progress' state
            control_count = self.env['control.quality'].search_count([
                ('of_id', '=', production.name),
                ('state', 'in', ['done', 'in_progress'])  # Include both 'done' and 'in_progress' states
            ])

            # Update the control_quality_done field
            production.control_quality_done = control_count

            # Update the quality_control_checked based on the count
            production.quality_control_checked = control_count > 0  # Set to True if count is greater than 0

    def action_return_components(self):
        for production in self:
            # Check if there are any components not consumed
            not_consumed_components = False

            # Get move lines for components (raw moves)
            for move in production.move_raw_ids:
                # Check if any quantity remains to be consumed
                if move.qty_left > 0:
                    not_consumed_components = True
                    break

            # If no unconsumed components, show warning in French and change state to cancel
            if not not_consumed_components:
                production.write({'state': 'cancel'})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Pas de composants à retourner'),
                        'message': _(
                            'Tous les composants ont été entièrement consommés. Il n\'y a pas de composants à retourner. L\'état de la production va changer à "Annulé" lors du rechargement de la page.'),
                        'sticky': True,
                        'type': 'warning',
                    }
                }

            # If there are unconsumed components, open the wizard
            return {
                'name': 'Return Components Wizard',
                'type': 'ir.actions.act_window',
                'res_model': 'return.components.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('nn_Z2S.view_return_components_wizard_form').id,
                'target': 'new',
                'context': {'default_mrp_production_id': production.id}
            }

    components_returned = fields.Boolean(string="Composants Retourné", default=False,
                                         compute='_compute_components_returned')

    @api.onchange('move_raw_ids.qty_left', 'move_raw_ids')
    def _compute_components_returned(self):
        for mrp in self:
            all_returned = True
            for move in mrp.move_raw_ids:
                if move.qty_left > 0:
                    all_returned = False
                    break
            mrp.components_returned = all_returned

    def action_view_return_operations(self):
        self.ensure_one()
        return {
            'name': 'Retour des Composants',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name), ('picking_type_id.sequence_code', '=', 'RT'),
                       ('state', '!=', 'done')],
            'type': 'ir.actions.act_window',
        }

        # Add 'all_returned' state

    def action_view_control_quality(self):
        for production in self:
            # Search for an existing control.quality record
            control_quality = self.env['control.quality'].search([
                ('of_id', '=', production.id),  # Use the ID of the production order (of_id)
                ('state', '=', 'done')
            ], limit=1)

            if control_quality:
                # Redirect to the existing quality control record
                return {
                    'name': 'Contrôle Qualité',
                    'type': 'ir.actions.act_window',
                    'res_model': 'control.quality',
                    'view_mode': 'form',
                    'res_id': control_quality.id,  # Open the existing record
                    'view_id': self.env.ref('nn_quality_control.view_quality_control_form').id,
                    # Redirect to specific view
                    'target': 'self'  # Open in the same window
                }
            else:
                # Generate a new reference and context for creating a new control quality record
                current_year = fields.Date.today().strftime('%y')
                sequence = self.env['ir.sequence'].next_by_code('control.quality') or '0001'
                reference = f"CQ - {current_year} - {sequence}"

                # Return action to create a new quality control record with specific view
                return {
                    'name': 'Créer Contrôle Qualité',
                    'type': 'ir.actions.act_window',
                    'res_model': 'control.quality',
                    'view_mode': 'form',
                    'view_id': self.env.ref('nn_quality_control.view_quality_control_form').id,
                    'target': 'self',
                    'context': {
                        'default_of_id': production.id,
                        'default_reference': reference,
                        'default_client_id': production.client_id.id,
                        'default_article_id': production.product_id.id,  # Add other fields here
                        'default_client_reference': production.ref_product_client,
                        'default_designation': production.description,
                        'default_qty_producing': production.product_qty,
                    }
                }

    @api.onchange('return_count')
    def _onchange_return_count(self):
        """Trigger the return components wizard with updated return_count when it changes."""
        if self.return_count:
            # Trigger the wizard with the updated return_count
            return {
                'name': 'Return Components Wizard',
                'type': 'ir.actions.act_window',
                'res_model': 'return.components.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('nn_Z2S.view_return_components_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_mrp_production_id': self.id,  # Pass the current production id
                    'default_return_count': self.return_count  # Pass the updated return count
                }
            }

#
