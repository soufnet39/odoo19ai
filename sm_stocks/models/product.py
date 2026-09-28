# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SMSalesProduct(models.Model):
    _inherit = 'sm_sales.product'

    rest_in_stock = fields.Float(
        string='Rest en stock',
        compute='_compute_rest_in_stock',
        digits='Quantity',
    )

    def _compute_rest_in_stock(self):
        stock_id = self.env.context.get('stock_id')
        exclude_order_id = self.env.context.get('exclude_order_id')

        physical = self.filtered(lambda p: p.product_type != 'service')
        (self - physical).rest_in_stock = 0.0

        if not physical:
            return

        domain = [
            ('product_id', 'in', physical.ids),
            ('stock_state', 'in', ('received', 'delivered')),
        ]
        if stock_id:
            domain.append(('stock_id', '=', stock_id))
        if exclude_order_id and isinstance(exclude_order_id, int):
            domain.append(('order_id', '!=', exclude_order_id))

        lines = self.env['sm_sales.order.line'].search(domain)
        qty_by_product = {}
        for line in lines:
            qty_by_product[line.product_id.id] = qty_by_product.get(line.product_id.id, 0.0) + (line.qty_value or 0.0)

        for product in physical:
            product.rest_in_stock = qty_by_product.get(product.id, 0.0)
