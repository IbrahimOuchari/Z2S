import logging

from odoo import api, models, _
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class QualityControl(models.Model):
    _inherit = 'control.quality'
    _description = 'Contrôle de Qualité'

    def action_detect_duplicates(self):
        """
        Action server function to detect duplicate Quality Control records
        for the same MRP production order from selected records in tree view
        """
        # Get selected records from context
        selected_ids = self.env.context.get('active_ids', [])
        if not selected_ids:
            raise UserError(_("Please select Quality Control records to check for duplicates."))

        selected_records = self.browse(selected_ids)

        # Group records by MRP production order (of_id)
        duplicates_by_of = {}
        for record in selected_records:
            if record.of_id:
                of_key = record.of_id.id
                if of_key not in duplicates_by_of:
                    duplicates_by_of[of_key] = []
                duplicates_by_of[of_key].append(record)

        # Find duplicates (more than one QC record for same OF)
        duplicates_found = {}
        for of_id, qc_records in duplicates_by_of.items():
            if len(qc_records) > 1:
                duplicates_found[of_id] = qc_records

        if not duplicates_found:
            raise UserError(_("No duplicate Quality Control records found for the same Manufacturing Order."))

        # Build message with duplicate information
        message = _("Duplicate Quality Control records found:\n\n")
        for of_id, qc_records in duplicates_found.items():
            of_record = self.env['mrp.production'].browse(of_id)
            message += f"Manufacturing Order: {of_record.name}\n"
            message += f"Product: {of_record.product_id.name}\n"
            message += f"Duplicate Quality Control records ({len(qc_records)}):\n"

            for qc in qc_records:
                message += f"  - {qc.reference} (ID: {qc.id})\n"
                message += f"    Type1 Lines: {len(qc.type1_line_ids)}\n"
                message += f"    Type2 Lines: {len(qc.type2_line_ids)}\n"
                message += f"    Type3 Lines: {len(qc.type3_line_ids)}\n"
                message += f"    State: {qc.state}\n"
            message += "\n"

        # Show message to user
        raise UserError(message)

    def action_merge_quality_controls(self):
        """
        Action server function to merge selected Quality Control records
        into a single record with combined line data
        """
        # Get selected records from context
        selected_ids = self.env.context.get('active_ids', [])
        if len(selected_ids) < 2:
            raise UserError(_("Please select at least 2 Quality Control records to merge."))

        selected_records = self.browse(selected_ids)

        # Validate that all records have the same of_id
        of_ids = selected_records.mapped('of_id')
        if len(of_ids) > 1:
            raise UserError(_("All selected Quality Control records must be for the same Manufacturing Order."))

        if not of_ids:
            raise UserError(_("Selected Quality Control records must have a Manufacturing Order assigned."))

        # Determine the base record (the one with most total lines)
        base_record = None
        max_lines = 0

        for record in selected_records:
            total_lines = len(record.type1_line_ids) + len(record.type2_line_ids) + len(record.type3_line_ids)
            if total_lines > max_lines:
                max_lines = total_lines
                base_record = record

        if not base_record:
            # If no lines exist, take the first record
            base_record = selected_records[0]

        # Collect all lines from all selected records
        all_type1_lines = []
        all_type2_lines = []
        all_type3_lines = []

        for record in selected_records:
            # Collect type1 lines
            for line in record.type1_line_ids:
                all_type1_lines.append({
                    'quality_id': base_record.id,
                    'serial_number': line.serial_number,
                    'result1': getattr(line, 'result1', False),
                    # Add other fields as needed based on your type1 line model
                })

            # Collect type2 lines
            for line in record.type2_line_ids:
                all_type2_lines.append({
                    'quality_id': base_record.id,
                    'serial_number': line.serial_number,
                    'result1': getattr(line, 'result1', False),
                    # Add other fields as needed based on your type2 line model
                })

            # Collect type3 lines
            for line in record.type3_line_ids:
                all_type3_lines.append({
                    'quality_id': base_record.id,
                    'serial_number': line.serial_number,
                    'result1': getattr(line, 'result1', False),
                    # Add other fields as needed based on your type3 line model
                })

        # Create new Quality Control record with merged data
        merged_record = self.create({
            'of_id': base_record.of_id.id,
            'type_1': bool(all_type1_lines),
            'type_2': bool(all_type2_lines),
            'type_3': bool(all_type3_lines),
            'controlleur_id': base_record.controlleur_id.id,
            'other_info': f"Merged from records: {', '.join(selected_records.mapped('reference'))}",
            'state': 'draft',
        })

        # Create the merged lines
        if all_type1_lines:
            # Remove duplicates based on serial_number, keeping the first occurrence
            unique_type1_lines = []
            seen_serials = set()
            for line_data in all_type1_lines:
                if line_data['serial_number'] not in seen_serials:
                    unique_type1_lines.append(line_data)
                    seen_serials.add(line_data['serial_number'])

            self.env['control.quality.type1.line'].create(unique_type1_lines)

        if all_type2_lines:
            # Remove duplicates based on serial_number, keeping the first occurrence
            unique_type2_lines = []
            seen_serials = set()
            for line_data in all_type2_lines:
                if line_data['serial_number'] not in seen_serials:
                    unique_type2_lines.append(line_data)
                    seen_serials.add(line_data['serial_number'])

            self.env['control.quality.type2.line'].create(unique_type2_lines)

        if all_type3_lines:
            # Remove duplicates based on serial_number, keeping the first occurrence
            unique_type3_lines = []
            seen_serials = set()
            for line_data in all_type3_lines:
                if line_data['serial_number'] not in seen_serials:
                    unique_type3_lines.append(line_data)
                    seen_serials.add(line_data['serial_number'])

            self.env['control.quality.type3.line'].create(unique_type3_lines)

        # Archive or delete the original records
        selected_records.write({'active': False})  # Archive them
        # Or use: selected_records.unlink()  # Delete them permanently

        # Show success message and open the merged record
        return {
            'type': 'ir.actions.act_window',
            'name': _('Merged Quality Control'),
            'res_model': 'control.quality',
            'res_id': merged_record.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_smart_merge_quality_controls(self):
        """
        Enhanced merge function that handles conflicts by choosing the record
        with more lines for each type
        """
        # Get selected records from context
        selected_ids = self.env.context.get('active_ids', [])
        if len(selected_ids) < 2:
            raise UserError(_("Please select at least 2 Quality Control records to merge."))

        selected_records = self.browse(selected_ids)

        # Validate that all records have the same of_id
        of_ids = selected_records.mapped('of_id')
        if len(of_ids) > 1:
            raise UserError(_("All selected Quality Control records must be for the same Manufacturing Order."))

        if not of_ids:
            raise UserError(_("Selected Quality Control records must have a Manufacturing Order assigned."))

        # For each type, find the record with the most lines
        best_type1_record = None
        best_type2_record = None
        best_type3_record = None

        max_type1_lines = 0
        max_type2_lines = 0
        max_type3_lines = 0

        for record in selected_records:
            type1_count = len(record.type1_line_ids)
            type2_count = len(record.type2_line_ids)
            type3_count = len(record.type3_line_ids)

            if type1_count > max_type1_lines:
                max_type1_lines = type1_count
                best_type1_record = record

            if type2_count > max_type2_lines:
                max_type2_lines = type2_count
                best_type2_record = record

            if type3_count > max_type3_lines:
                max_type3_lines = type3_count
                best_type3_record = record

        # Use the first record as base for other fields
        base_record = selected_records[0]

        # Create new Quality Control record with merged data
        merged_record = self.create({
            'of_id': base_record.of_id.id,
            'type_1': bool(best_type1_record and max_type1_lines > 0),
            'type_2': bool(best_type2_record and max_type2_lines > 0),
            'type_3': bool(best_type3_record and max_type3_lines > 0),
            'controlleur_id': base_record.controlleur_id.id,
            'other_info': f"Smart merged from records: {', '.join(selected_records.mapped('reference'))}",
            'state': 'draft',
        })

        # Copy lines from the best records for each type
        if best_type1_record and max_type1_lines > 0:
            for line in best_type1_record.type1_line_ids:
                line.copy({'quality_id': merged_record.id})

        if best_type2_record and max_type2_lines > 0:
            for line in best_type2_record.type2_line_ids:
                line.copy({'quality_id': merged_record.id})

        if best_type3_record and max_type3_lines > 0:
            for line in best_type3_record.type3_line_ids:
                line.copy({'quality_id': merged_record.id})

        # Archive the original records
        selected_records.write({'active': False})

        # Show success message and open the merged record
        return {
            'type': 'ir.actions.act_window',
            'name': _('Smart Merged Quality Control'),
            'res_model': 'control.quality',
            'res_id': merged_record.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_analyze_duplicates_detailed(self):
        """
        Detailed analysis of duplicates with recommendations
        """
        # Get selected records from context
        selected_ids = self.env.context.get('active_ids', [])
        if not selected_ids:
            raise UserError(_("Please select Quality Control records to analyze."))

        selected_records = self.browse(selected_ids)

        # Group records by MRP production order (of_id)
        duplicates_by_of = {}
        for record in selected_records:
            if record.of_id:
                of_key = record.of_id.id
                if of_key not in duplicates_by_of:
                    duplicates_by_of[of_key] = []
                duplicates_by_of[of_key].append(record)

        # Find duplicates and analyze them
        analysis_results = []
        for of_id, qc_records in duplicates_by_of.items():
            if len(qc_records) > 1:
                of_record = self.env['mrp.production'].browse(of_id)

                # Analyze the duplicates
                analysis = {
                    'of_name': of_record.name,
                    'of_product': of_record.product_id.name,
                    'records': [],
                    'recommendations': []
                }

                total_type1_lines = 0
                total_type2_lines = 0
                total_type3_lines = 0

                for qc in qc_records:
                    record_info = {
                        'reference': qc.reference,
                        'id': qc.id,
                        'state': qc.state,
                        'type1_lines': len(qc.type1_line_ids),
                        'type2_lines': len(qc.type2_line_ids),
                        'type3_lines': len(qc.type3_line_ids),
                        'total_lines': len(qc.type1_line_ids) + len(qc.type2_line_ids) + len(qc.type3_line_ids)
                    }
                    analysis['records'].append(record_info)

                    total_type1_lines += record_info['type1_lines']
                    total_type2_lines += record_info['type2_lines']
                    total_type3_lines += record_info['type3_lines']

                # Generate recommendations
                if total_type1_lines > 0 and total_type2_lines > 0 and total_type3_lines > 0:
                    analysis['recommendations'].append("All types have data - consider smart merge")
                elif any(r['total_lines'] > 0 for r in analysis['records']):
                    analysis['recommendations'].append("Some records have data - merge recommended")
                else:
                    analysis['recommendations'].append("No line data found - consider deletion")

                analysis_results.append(analysis)

        if not analysis_results:
            raise UserError(_("No duplicate Quality Control records found."))

        # Build detailed report
        report = _("=== QUALITY CONTROL DUPLICATES ANALYSIS ===\n\n")

        for analysis in analysis_results:
            report += f"Manufacturing Order: {analysis['of_name']}\n"
            report += f"Product: {analysis['of_product']}\n"
            report += f"Number of duplicate QC records: {len(analysis['records'])}\n\n"

            report += "Records Details:\n"
            for record in analysis['records']:
                report += f"  • {record['reference']} (ID: {record['id']})\n"
                report += f"    State: {record['state']}\n"
                report += f"    Type1 Lines: {record['type1_lines']}\n"
                report += f"    Type2 Lines: {record['type2_lines']}\n"
                report += f"    Type3 Lines: {record['type3_lines']}\n"
                report += f"    Total Lines: {record['total_lines']}\n\n"

            report += "Recommendations:\n"
            for rec in analysis['recommendations']:
                report += f"  → {rec}\n"

            report += "\n" + "=" * 50 + "\n\n"

        # Show detailed report
        raise UserError(report)
