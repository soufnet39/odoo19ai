# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_number = fields.Integer(string='#', compute='_compute_line_number')

    def _compute_line_number(self):
        for order in self.mapped('order_id'):
            for i, line in enumerate(order.order_line.sorted('sequence'), 1):
                line.line_number = i


