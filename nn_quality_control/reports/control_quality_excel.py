import xlsxwriter
from io import BytesIO
from odoo import models
from odoo.exceptions import UserError

class QualityControlReport(models.AbstractModel):
    _name = 'report.nn_quality_control.quality_control_report_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, quality_control):
        sheet = workbook.add_worksheet("Rapport de Contrôle Qualité")
        # Set column widths for better readability
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 50)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 25)

        # Define formats
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#D9EAD3'})
        cell_format = workbook.add_format({'align': 'center'})
        date_format = workbook.add_format({'align': 'center', 'num_format': 'yyyy-mm-dd hh:mm:ss'})

        # Write header for the report
        sheet.write('A1', 'Rapport de Contrôle Qualité', header_format)
        sheet.write('A2', 'ID Contrôle Qualité', header_format)
        sheet.write('B2', quality_control.reference, cell_format)

        row = 5
        # Write additional fields to the report
        sheet.write('A' + str(row), 'Contrôleur', header_format)
        sheet.write('B' + str(row), quality_control.controlleur_id.name if quality_control.controlleur_id else '',
                    cell_format)
        row += 1

        sheet.write('A' + str(row), 'Date de début', header_format)
        sheet.write('B' + str(row),
                    quality_control.start_date.strftime('%Y-%m-%d') if quality_control.start_date else '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Date de fin', header_format)
        sheet.write('B' + str(row), quality_control.end_date.strftime('%Y-%m-%d') if quality_control.end_date else '',
                    cell_format)
        row += 1
        sheet.write('A' + str(row), 'Code-barres', header_format)
        sheet.write('B' + str(row), quality_control.barcode or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Référence', header_format)
        sheet.write('B' + str(row), quality_control.reference or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Ordre de Fabrication', header_format)
        sheet.write('B' + str(row), quality_control.of_id.name if quality_control.of_id else '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'ID Article', header_format)
        sheet.write('B' + str(row), quality_control.article_id.name if quality_control.article_id else '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Référence Client', header_format)
        sheet.write('B' + str(row), quality_control.client_reference or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Client', header_format)
        sheet.write('B' + str(row), quality_control.client_id.name if quality_control.client_id else '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Désignation', header_format)
        sheet.write('B' + str(row), quality_control.designation or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Quantité en Production', header_format)
        sheet.write('B' + str(row), quality_control.qty_producing, cell_format)
        row += 1
        sheet.write('A' + str(row), 'Nombre Total de Lignes', header_format)
        sheet.write('B' + str(row), quality_control.total_lines, cell_format)
        row += 1
        sheet.write('A' + str(row), 'Autres Informations', header_format)
        sheet.write('B' + str(row), quality_control.other_info or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'PPM', header_format)
        sheet.write('B' + str(row), quality_control.ppm or '', cell_format)
        row += 1
        sheet.write('A' + str(row), 'Taux de Défaut Global', header_format)
        sheet.write('B' + str(row), quality_control.global_defect_rate or '', cell_format)
        row += 5

        if quality_control.type1_line_ids:
            def add_summary_section(row, label, conform, non_conform, total_default, taux_default):
                sheet.write(row, 0, label, header_format)
                sheet.write(row, 1, 'Nombre Conforme', header_format)
                sheet.write(row, 2, conform, cell_format)
                sheet.write(row + 1, 1, 'Nombre Non Conforme', header_format)
                sheet.write(row + 1, 2, non_conform, cell_format)
                sheet.write(row + 2, 1, 'Total Défauts Client', header_format)
                sheet.write(row + 2, 2, total_default, cell_format)
                sheet.write(row + 3, 1, 'Taux de Défaut %', header_format)
                sheet.write(row + 3, 2, taux_default, cell_format)
                return row + 5

            row += 1
            row = add_summary_section(row, 'Contrôle lampe loupe',
                                      quality_control.type1_conform_count,
                                      quality_control.type1_non_conform_count,
                                      quality_control.type1_total_client_default,
                                      quality_control.type1_client_default_avg)

            sheet.write('A' + str(row + 1), 'Numéro de Série', header_format)
            sheet.write('B' + str(row + 1), 'Contrôleur', header_format)
            sheet.write('C' + str(row + 1), 'Opérateur', header_format)
            sheet.write('D' + str(row + 1), 'Nombre de Services', header_format)
            sheet.write('E' + str(row + 1), 'Résultat 1', header_format)
            sheet.write('F' + str(row + 1), 'Type de Défaut', header_format)
            sheet.write('G' + str(row + 1), 'Reprise', header_format)
            sheet.write('H' + str(row + 1), 'Autres Informations', header_format)
            row += 1

            for line in quality_control.type1_line_ids:
                sheet.write(row, 0, line.serial_number, cell_format)
                sheet.write(row, 1, line.controlleur_id.name if line.controlleur_id else '', cell_format)
                sheet.write(row, 2, line.operator_id.name if line.operator_id else '', cell_format)
                sheet.write(row, 3, line.service_count, cell_format)
                sheet.write(row, 4, line.result1, cell_format)
                sheet.write(row, 5, line.defect1.name if line.defect1 else '', cell_format)
                sheet.write(row, 6, line.reprise_id.name if line.reprise_id else '', cell_format)
                sheet.write(row, 7, line.other_info, cell_format)
                row += 1

        row += 5
        if quality_control.type2_line_ids:
            def add_summary_section(row, label, conform, non_conform, total_default, taux_default):
                sheet.write(row, 0, label, header_format)
                sheet.write(row, 1, 'Nombre Conforme', header_format)
                sheet.write(row, 2, conform, cell_format)
                sheet.write(row + 1, 1, 'Nombre Non Conforme', header_format)
                sheet.write(row + 1, 2, non_conform, cell_format)
                sheet.write(row + 2, 1, 'Total Défauts Client', header_format)
                sheet.write(row + 2, 2, total_default, cell_format)
                sheet.write(row + 3, 1, 'Taux de Défaut %', header_format)
                sheet.write(row + 3, 2, taux_default, cell_format)
                return row + 5

            row += 1
            row = add_summary_section(row, 'Contrôle Caméra',
                                      quality_control.type2_conform_count,
                                      quality_control.type2_non_conform_count,
                                      quality_control.type2_total_client_default,
                                      quality_control.type2_client_default_avg)

            sheet.write('A' + str(row + 1), 'Numéro de Série', header_format)
            sheet.write('B' + str(row + 1), 'Contrôleur', header_format)
            sheet.write('C' + str(row + 1), 'Opérateur', header_format)
            sheet.write('D' + str(row + 1), 'Nombre de Services', header_format)
            sheet.write('E' + str(row + 1), 'Résultat 1', header_format)
            sheet.write('F' + str(row + 1), 'Type de Défaut', header_format)
            sheet.write('G' + str(row + 1), 'Reprise', header_format)
            sheet.write('H' + str(row + 1), 'Autres Informations', header_format)
            row += 1

            for line in quality_control.type2_line_ids:
                sheet.write(row, 0, line.serial_number, cell_format)
                sheet.write(row, 1, line.controlleur_id.name if line.controlleur_id else '', cell_format)
                sheet.write(row, 2, line.operator_id.name if line.operator_id else '', cell_format)
                sheet.write(row, 3, line.service_count, cell_format)
                sheet.write(row, 4, line.result1, cell_format)
                sheet.write(row, 5, line.defect1.name if line.defect1 else '', cell_format)
                sheet.write(row, 6, line.reprise_id.name if line.reprise_id else '', cell_format)
                sheet.write(row, 7, line.other_info, cell_format)
                row += 1

        row += 5
        if quality_control.type3_line_ids:
            def add_summary_section(row, label, conform, non_conform, total_default, taux_default):
                sheet.write(row, 0, label, header_format)
                sheet.write(row, 1, 'Nombre Conforme', header_format)
                sheet.write(row, 2, conform, cell_format)
                sheet.write(row + 1, 1, 'Nombre Non Conforme', header_format)
                sheet.write(row + 1, 2, non_conform, cell_format)
                sheet.write(row + 2, 1, 'Total Défauts Client', header_format)
                sheet.write(row + 2, 2, total_default, cell_format)
                sheet.write(row + 3, 1, 'Taux de Défaut %', header_format)
                sheet.write(row + 3, 2, taux_default, cell_format)
                return row + 5

            row += 1
            row = add_summary_section(row, 'Contrôle Rayon X',
                                      quality_control.type3_conform_count,
                                      quality_control.type3_non_conform_count,
                                      quality_control.type3_total_client_default,
                                      quality_control.type3_client_default_avg)

            sheet.write('A' + str(row + 1), 'Numéro de Série', header_format)
            sheet.write('B' + str(row + 1), 'Contrôleur', header_format)
            sheet.write('C' + str(row + 1), 'Opérateur', header_format)
            sheet.write('D' + str(row + 1), 'Nombre de Services', header_format)
            sheet.write('E' + str(row + 1), 'Résultat 1', header_format)
            sheet.write('F' + str(row + 1), 'Type de Défaut', header_format)
            sheet.write('G' + str(row + 1), 'Reprise', header_format)
            sheet.write('H' + str(row + 1), 'Autres Informations', header_format)
            row += 1

            for line in quality_control.type3_line_ids:
                sheet.write(row, 0, line.serial_number, cell_format)
                sheet.write(row, 1, line.controlleur_id.name if line.controlleur_id else '', cell_format)
                sheet.write(row, 2, line.operator_id.name if line.operator_id else '', cell_format)
                sheet.write(row, 3, line.service_count, cell_format)
                sheet.write(row, 4, line.result1, cell_format)
                sheet.write(row, 5, line.defect1.name if line.defect_type_id else '', cell_format)
                sheet.write(row, 6, line.reprise_id.name if line.reprise_id else '', cell_format)
                sheet.write(row, 7, line.other_info, cell_format)
                row += 1