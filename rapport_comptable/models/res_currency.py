# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    excel_format = fields.Char(string='Format Excel', default='_ * #,##0.00_) ;_ * - #,##0.00_) ;_ * "-"??_) ;_ @_ ', required=True)
