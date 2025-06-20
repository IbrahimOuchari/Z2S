import logging
import math

from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LabelManagement(models.Model):
    _name = 'label.management'
    _description = 'Label Management'

    name = fields.Char(copy=False, unique=True)
    finished_product_id = fields.Many2one('product.product', string="Produit Fini")
    client_reference = fields.Char(string="Référence Client")
    designation = fields.Char(string="Désignation")
    manufacturing_order_id = fields.Many2one('mrp.production', string="Numéro OF", ondelete='cascade')
    num_lot = fields.Integer(string="Numéro de Lot", compute='_compute_num_lot', store=True)
    cumule = fields.Float(string="Cumulé", compute='_compute_cumule', store=True, digits=(16, 0))
    quantity_per_batch = fields.Float(string="Quantité colisage", required=True, digits=(16, 0))
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking")  # Existing relation to Stock Picking
    related_of = fields.Many2one('mrp.production', string="Manufacturing Order")
    active = fields.Boolean(string="Actif", default=True)  # State to manage active lots
    total_quantity_per_batch = fields.Float(string="Total Quantité par Lot",
                                            compute='_compute_total_quantity_per_batch', store=True)
    state = fields.Selection([
        ('conforme', 'Conforme'),
        ('non-conforme', 'Non Conforme')
    ], string="État", default='conforme', required=True)
    is_readonly_lot = fields.Boolean(string="Readonly Lot", default=False)

    stock_move_id = fields.Many2one('stock.move', string="Mouvement de stock", ondelete='cascade')

    # date = fields.Date(string="Date")

    def _compute_my_field_readonly(self):
        return not (
            self.user.has_group("nn_Z2S.lot_date_edit")
        )

    date = fields.Date(string="Date",
                       readonly=_compute_my_field_readonly,
                       )

    @api.depends('quantity_per_batch')
    def _compute_total_quantity_per_batch(self):
        for record in self:
            total = sum(line.quantity_per_batch for line in self.search([
                ('manufacturing_order_id', '=', record.manufacturing_order_id.id),
                ('active', '=', True)  # Check only active lots
            ]))
            record.total_quantity_per_batch = total

    @api.depends('quantity_per_batch', 'manufacturing_order_id')
    def _compute_num_lot(self):
        for record in self:
            if record.quantity_per_batch > 0 and record.manufacturing_order_id.qty_producing:
                qty_producing = record.manufacturing_order_id.qty_producing
                lot_size = record.quantity_per_batch
                record.num_lot = math.ceil(qty_producing / lot_size)
            else:
                record.num_lot = 0

    @api.onchange('quantity_per_batch')
    def _onchange_quantity_per_batch(self):
        if self.manufacturing_order_id:
            related_records = self.search([
                ('manufacturing_order_id', '=', self.manufacturing_order_id.id),
                ('active', '=', True)  # Check only active lots
            ])
            for record in related_records:
                record._compute_cumule()  # Recalculate cumule for each related record
        self._compute_cumule()  # Recalculate cumule for the current record

    @api.depends('quantity_per_batch', 'manufacturing_order_id')
    def _compute_cumule(self):
        for record in self:
            if record.manufacturing_order_id:
                total_cumule = 0.0
                related_records = self.search([
                    ('manufacturing_order_id', '=', record.manufacturing_order_id.id),
                    ('active', '=', True)  # Check only active lots
                ])
                for rel_record in related_records:
                    total_cumule += rel_record.quantity_per_batch
                    rel_record.cumule = total_cumule  # Update cumule for each related record

    @api.model
    def create_lots_for_order(self, manufacturing_order, qty_producing):
        qty_per_batch = manufacturing_order.quantity_per_batch
        total_qty = qty_producing

        if qty_per_batch <= 0:
            raise ValueError("La quantité par lot doit être supérieure à zéro.")

        existing_lines = self.search([
            ('manufacturing_order_id', '=', manufacturing_order.id),
            ('active', '=', True)  # Check only active lots
        ])
        existing_lines.write({'active': False})  # Deactivate existing lots for the current order

        num_lots = math.ceil(total_qty / qty_per_batch)
        cumule = 0.0

        for i in range(num_lots):
            if i == num_lots - 1:  # Last lot
                lot_qty = total_qty - (qty_per_batch * i)
            else:
                lot_qty = qty_per_batch

            cumule += lot_qty

            sequence_number = self.env['ir.sequence'].next_by_code('label_management.of_exp_year.sequence')

            # Use the same year calculation
            lot_name = f"{sequence_number}"
            # Create the lot with name format "ID-ETQ-EXP"
            self.create({
                'finished_product_id': manufacturing_order.product_id.id,
                'quantity_per_batch': lot_qty,
                'manufacturing_order_id': manufacturing_order.id,
                'num_lot': i + 1,
                'cumule': cumule,
                'name': lot_name,  # Set the name here
                'active': True,
            })

    def create_lots_for_stock_move(self, move, qty_done):
        qty_per_batch = move.quantity_per_batch
        total_qty = move.quantity_done

        # Debugging outputs
        print(f"Qty per batch: {qty_per_batch}")
        print(f"Total qty: {total_qty}")

        if qty_per_batch <= 0:
            raise ValueError("La quantité par lot doit être supérieure à zéro.")

        # Deactivate existing lots for the stock move
        existing_lines = self.search([
            ('stock_move_id', '=', move.id),
            ('active', '=', True)  # Check only active lots
        ])
        existing_lines.write({'active': False})

        num_lots = math.ceil(total_qty / qty_per_batch)

        # Debugging output
        print(f"Number of lots to create: {num_lots}")

        if num_lots <= 0:
            print("No lots to create.")
            return

        cumule = 0.0

        for i in range(num_lots):
            if i == num_lots - 1:
                lot_qty = total_qty - (qty_per_batch * i)
            else:
                lot_qty = qty_per_batch

            cumule += lot_qty
            year = fields.Date.today().year % 100

            # Create the lot with name format "REC or EXP-YEAR-XXXX"
            # prefix = 'REC' if move.picking_type_code == 'incoming' else 'EXP'
            if move.picking_type_code == 'incoming':
                sequence_number = self.env['ir.sequence'].next_by_code('label_management.rec_a.sequence')

                lot_name = sequence_number  # Format name correctly
                self.create({
                    'quantity_per_batch': lot_qty,
                    'stock_move_id': move.id,
                    'cumule': cumule,
                    'name': lot_name,  # Set the name here
                    'active': True,
                })
            elif move.picking_type_code == 'internal':
                _logger.info("📌 RT condition matched")
                _logger.info(f"🧾 Stock Move ID: {move.id}")
                _logger.info(f"🛠 Picking Type Code: {move.picking_type_code}")
                _logger.info(f"🔢 Picking Type Sequence: {move.picking_type_id.sequence}")
                _logger.info(f"🎯 Lot Quantity: {lot_qty}")
                _logger.info(f"📊 Cumulative Quantity: {cumule}")

                sequence_number = self.env['ir.sequence'].next_by_code('label_management.ret_int_op.sequence')
                lot_name = sequence_number
                _logger.info(f"📦 Generated Sequence: {lot_name}")

                # Create the lot and store the result
                new_lot = self.create({
                    'quantity_per_batch': lot_qty,
                    'stock_move_id': move.id,
                    'cumule': cumule,
                    'name': lot_name,
                    'active': True,
                })

                # Log the outcome
                _logger.info(f"✅ Lot created with ID: {new_lot.id} and Name: {new_lot.name}")

            elif move.picking_type_code == 'outgoing':
                # Use the same year calculation
                sequence_number = self.env['ir.sequence'].next_by_code('label_management.of_exp_year.sequence')

                lot_name = sequence_number  # Format name correctly

                self.create({
                    'quantity_per_batch': lot_qty,
                    'stock_move_id': move.id,
                    'cumule': cumule,
                    'name': lot_name,  # Set the name here
                    'active': True,
                })

    @api.constrains('quantity_per_batch', 'manufacturing_order_id')
    def _check_quantity_per_batch(self):
        for record in self:
            if record.manufacturing_order_id and record.quantity_per_batch:
                produced_qty = record.manufacturing_order_id.qty_producing
                if record.quantity_per_batch <= 0:
                    raise ValidationError("La quantité par lot doit être supérieure à zéro.")
                if record.quantity_per_batch > produced_qty:
                    raise ValidationError(
                        "La quantité par lot ({}) ne peut pas dépasser la quantité produite ({}).".format(
                            record.quantity_per_batch, produced_qty
                        )
                    )
                if record.total_quantity_per_batch > produced_qty:
                    raise ValidationError(
                        "La somme des quantités par lot ({}) ne peut pas dépasser la quantité produite ({}).".format(
                            record.total_quantity_per_batch, produced_qty
                        )
                    )

    def create(self, vals):
        # Handle batch creation
        if isinstance(vals, list):
            # This is a batch create
            records = []
            for val in vals:
                record = self._prepare_create_values(val)
                records.append(super(LabelManagement, self).create(record))
            return records  # Return a list of created records

        # Handle single creation
        record = self._prepare_create_values(vals)
        return super(LabelManagement, self).create(record)

    def _prepare_create_values(self, vals):
        manufacturing_order_id = vals.get('manufacturing_order_id')
        stock_move_id = vals.get('stock_move_id')
        year = fields.Date.today().year % 100  # Get the last two digits of the year
        vals['date'] = fields.Date.today()  # Set the current date

        # Debugging output
        print(f"Preparing to create LabelManagement record with vals: {vals}")

        # Generate sequence number based on the context (REC-A, REC-F, or EXP)
        if stock_move_id:
            # Handle stock moves
            stock_move = self.env['stock.move'].browse(stock_move_id)
            picking_type = stock_move.picking_type_code

            if picking_type == 'incoming':  # REC-A or REC-F
                # Check if the product has purchase_ok == True
                if stock_move.product_id.purchase_ok:  # If the product can be purchased, use REC-A sequence
                    sequence_number = self.env['ir.sequence'].next_by_code('label_management.rec_a.sequence')
                    if not sequence_number:
                        raise ValueError("Sequence number for REC-A could not be generated.")
                else:
                    sequence_number = self.env['ir.sequence'].next_by_code('label_management.rec_f.sequence')
                    if not sequence_number:
                        raise ValueError("Sequence number for REC-F could not be generated.")

                # Construct the name using the selected sequence
                name = f"{sequence_number}"

            elif picking_type == 'internal':  # Outgoing, use EXP
                sequence_number = self.env['ir.sequence'].next_by_code('label_management.ret_int_op.sequence')
                if not sequence_number:
                    raise ValueError("Sequence number for EXP could not be generated.")
                name = f"{sequence_number}"
            elif picking_type == 'outgoing':  # Outgoing, use EXP
                sequence_number = self.env['ir.sequence'].next_by_code('label_management.of_exp_year.sequence')
                if not sequence_number:
                    raise ValueError("Sequence number for EXP could not be generated.")
                name = f"{sequence_number}"

            # Ensure uniqueness of the name
            counter = 1
            original_name = name
            while self.search_count([('name', '=', name), ('stock_move_id', '=', stock_move_id)]) > 0:
                name = f"{original_name}-{counter}"  # Add a counter suffix if name already exists
                counter += 1

            vals['name'] = name

        elif manufacturing_order_id:
            # Handle manufacturing orders
            production_order = self.env['mrp.production'].browse(manufacturing_order_id)

            # Use the specified sequence for manufacturing orders
            sequence_number = self.env['ir.sequence'].next_by_code('label_management.of_exp_year.sequence')
            if not sequence_number:
                raise ValueError("Sequence number for manufacturing order could not be generated.")

            # Construct the name using the specified sequence
            vals['name'] = sequence_number

            # Ensure uniqueness of the name
            counter = 1
            original_name = vals['name']
            while self.search_count(
                    [('name', '=', vals['name']), ('manufacturing_order_id', '=', manufacturing_order_id)]) > 0:
                vals['name'] = f"{original_name}-{counter}"  # Add a counter suffix if name already exists
                counter += 1

        else:
            # If no stock_move_id or manufacturing_order_id is provided, generate a default name
            default_name = f"DEFAULT-{year}-{fields.Date.today().strftime('%Y%m%d')}-{self.env['ir.sequence'].next_by_code('label_management.default.sequence') or '0000'}"
            vals['name'] = default_name

        return vals

    def print_label(self):
        """Print the label for a single record."""
        # Ensure there is only one label to generate the report
        self.ensure_one()

        # Fetch the report using the reference defined in XML
        report = self.env.ref('nn_Z2S.action_label_management_report')

        # Generate the report for the current LabelManagement record
        return report.report_action(self)

    def print_label_stock_move(self):
        """Print the label for a single record."""
        # Ensure there is only one label to generate the report
        self.ensure_one()

        # Fetch the report using the reference defined in XML
        report = self.env.ref('nn_Z2S.action_label_management_stock_move_report')

        # Generate the report for the current LabelManagement record
        return report.report_action(self)
