# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class SmStocksOrder(models.Model):
    _inherit = 'sm_sales.order'

    @api.model
    def _default_stock_id(self):
        stocks = self.env['sm_stocks.stock'].search([])
        return stocks.id if len(stocks) == 1 else False

    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', required=True, tracking=True, default=_default_stock_id)
    is_received_delivered= fields.Boolean('Is received or delivered')
    date_stk_in_out=fields.Date("Date Stock")
    note_stock = fields.Html('Note Stock')
    stock_state = fields.Selection([
            ('pending', 'En attente'),
            ('received', 'Reçu'),
            ('delivered', 'Livré'),
            ('returned', 'Retourné'),],
            string='Etat', readonly=True, copy=False, index=True, tracking=3,
            default='pending', required=True )

    delivery_confirmed_by_default = fields.Boolean(
        string='Delivery Confirmed by Default',
        compute='_compute_confirmed_by_default',
    )
    reception_confirmed_by_default = fields.Boolean(
        string='Reception Confirmed by Default',
        compute='_compute_confirmed_by_default',
    )


    @api.depends()
    def _compute_confirmed_by_default(self):
        icp = self.env['ir.config_parameter'].sudo()
        for order in self:
            order.delivery_confirmed_by_default = icp.get_param('sm_stocks.delivery_confirmed_by_default', 'False').lower() == 'true'
            order.reception_confirmed_by_default = icp.get_param('sm_stocks.reception_confirmed_by_default', 'False').lower() == 'true'

    #TODO::SEE THIS 
    def _default_document_type(self):
            # a = self._context.get("default_operation_type") == 'order' and self.env['ir.config_parameter'].sudo().get_param('sm_stocks.delivery_confirmed_by_default')
            # b = self._context.get("default_operation_type") == 'purchase' and self.env['ir.config_parameter'].sudo().get_param('sm_stocks.reception_confirmed_by_default')
            if self.operation_type=='order': 
                return 'livraison'
            if self.operation_type=='purchase':
                return 'reception'
            return ''
    
    document_type = fields.Selection([
        ('livraison', 'Livraison'),
        ('reception', 'Recéption'),
        ('sortie', 'Bon de sortie'),
        ('entree', 'Bon d\'entrée'),
    ],
        string='Type de document', copy=False, default=_default_document_type  )
    
    def create(self, vals_list):
        res = super(SmStocksOrder, self).create(vals_list)
        for order in res:
            order.date_stk_in_out=order.date
            if order.delivery_confirmed_by_default and order.operation_type=='order':
                order.stock_state='delivered'
                for line in order.order_lines:                    
                    line.qty_value = -line.qty
            if order.reception_confirmed_by_default and order.operation_type=='purchase':
                order.stock_state='received'
                for line in order.order_lines:                   
                    line.qty_value = line.qty
        return res
    
    # def write(self, vals):
    #     res = super(SmStocksOrder, self).write(vals)
    #     for order in self:
    #         if order.delivery_confirmed_by_default and order.operation_type=='order':
    #             for line in order.order_lines:
    #                 line.qty_value = -line.qty
    #         if order.reception_confirmed_by_default and order.operation_type=='purchase':
    #             for line in order.order_lines:                 
    #                 line.qty_value = line.qty
    #     return res
   
    def action_delivered(self):
        for order in self:
            order.stock_state='delivered'           
   
    def action_delivered_returned(self):
        for order in self:
            order.stock_state='returned'

    def action_print_deliver(self):
        return self.env.ref('sm_stocks.action_report_delivery').report_action(self)

    def action_received(self):
        for order in self:
            order.stock_state='received'
           
    def action_received_returned(self):
        for order in self:
            order.stock_state='returned'
           
    def action_print_received(self):
        return self.env.ref('sm_stocks.action_report_receipt').report_action(self)

    

    def action_confirm(self):
        for order in self:
            violation = order.order_lines._stock_rule_violation()
            if violation:
                line, total_qty, rest = violation
                raise UserError(_(
                    "Stock insuffisant pour %s. \n %s disponible(s) en stock. \n %s demandé(s)."
                ) % (line.product_id.name, int(rest), int(total_qty)))
        return super(SmStocksOrder, self).action_confirm()
    def go_deliver(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Livraison'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sm_stocks.sm_stocks_delivery_form').id,
            'target': 'current',
        }
    def go_commande(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': _('Commande'),
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'view_id': self.env.ref('sm_sales.view_sm_sales_order_form').id,
                'target': 'current',
            }
    def go_receipt(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Réception'),
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('sm_stocks.sm_stocks_receipt_form').id,
            'target': 'current',
        }
    def go_achat(self):
                self.ensure_one()
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Achat'),
                    'res_model': self._name,
                    'res_id': self.id,
                    'view_mode': 'form',
                    'view_id': self.env.ref('sm_purchases.view_sm_purchases_purchase_form').id,
                    'target': 'current',
                }


class SmStocksOrderLines(models.Model):
    _inherit = 'sm_sales.order.line'

    
    qty_value = fields.Float(string='Qte. Valeur', digits="Quantity", compute="_compute_qty_value", store=True  )
    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', related='order_id.stock_id', store=True, readonly=True)
    is_not_delivered = fields.Boolean(compute='_compute_delivery_status', store=True)
    is_not_received = fields.Boolean(compute='_compute_received_status', store=True)
    document_type= fields.Selection(related='order_id.document_type', string='Type de document', store=True, readonly=True)
    stock_state= fields.Selection(related='order_id.stock_state', string='Etat', store=True, readonly=True)
    rest_in_stock = fields.Float(
        string='Rest en stock',
        compute='_compute_rest_in_stock',
        digits='Quantity',
    )

    @api.depends("qty")
    def _compute_qty_value(self):
        for line in self:
            if line.order_id.operation_type == 'order':
                line.qty_value = -line.qty
            elif line.order_id.operation_type == 'purchase':
                line.qty_value = line.qty
                
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
            # Exclude the current order's own lines so the rest reflects the
            # physical on-hand BEFORE this order (auto-delivery already reduces
            # stock on create, which would otherwise double-count at confirm).
            if line.order_id:
                domain.append(('order_id', '!=', line.order_id.id))
            lines = self.env['sm_sales.order.line'].search(domain)           
            line.rest_in_stock = sum(l.qty_value for l in lines)

    def _stock_rule_violation(self):
        """Return (line, total_qty, rest) if the line violates the stock rule, else False."""
        for line in self:
            order = line.order_id
            if order.operation_type != 'order': # purchases are valid always
                continue
            if not line.product_id or not line.stock_id:
                continue
            if line.product_id.product_type != 'consu': # like service it is endless
                continue
            if line.stock_id.can_be_negatif:
                continue
            total_qty = sum(
                l.qty for l in order.order_lines
                if l.product_id == line.product_id and l.stock_id == line.stock_id and l.id != line.id
            )
            if total_qty > line.rest_in_stock:
                return (line, total_qty, line.rest_in_stock)
        return False

    @api.onchange('product_id', 'qty')
    def _onchange_check_stock(self):
        violation = self._stock_rule_violation()
        if violation:
            line, total_qty, rest = violation
            raise UserError(_(
                 "Stock insuffisant pour %s. \n %s disponible(s) en stock. \n %s demandé(s)."
            ) % (line.product_id.name, int(rest), int(total_qty)))

    @api.constrains('qty', 'product_id', 'stock_id')
    def _check_stock_available(self):
        violation = self._stock_rule_violation()
        if violation:
            line, total_qty, rest = violation
            raise UserError(_(
                 "Stock insuffisant pour %s. \n %s disponible(s) en stock. \n %s demandé(s)."
            ) % (line.product_id.name, int(rest), int(total_qty)))

   

    # def write(self, vals):
    #     res = super(SmStocksOrderLines, self).write(vals)
    #     for line in self:
    #         if line.order_id.operation_type == 'order':
    #             line.qty_value = -line.qty
    #         elif line.order_id.operation_type == 'purchase':
    #             line.qty_value = line.qty
    #     return res
    