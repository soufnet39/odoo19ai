# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SmStocksQuotation(models.Model):
    _inherit = 'sm_sales.quotation'

    @api.model
    def _default_stock_id(self):
        stocks = self.env['sm_stocks.stock'].search([])
        return stocks.id if len(stocks) == 1 else False
    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', required=True, tracking=True, default=_default_stock_id)


class SmStocksQuotationLines(models.Model):
    _inherit = 'sm_sales.quotation.line'

    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', related='quotation_id.stock_id', store=True, readonly=True)

    rest_in_stock = fields.Float(
            string='Rest en stock',
            compute='_compute_rest_in_stock',
            digits='Quantity',
        )
    
    @api.depends('product_id', 'stock_id',"qty")
    def _compute_rest_in_stock(self):
        for line in self:
            if not line.product_id or not line.stock_id:
                line.rest_in_stock = 0.0
                continue
            domain = [
                ('product_id', '=', line.product_id.id),
                ('stock_id', '=', line.stock_id.id),
            ]
    
            lines = self.env['sm_sales.order.line'].search(domain)           
            line.rest_in_stock = sum(l.qty_value for l in lines)