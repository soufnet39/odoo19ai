# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class SmStocksStockMovement(models.Model):
    _name = 'sm_stocks.stock.movement'
    _description = 'Mouvement de stock'
    _auto = False
    _order = 'date desc, id desc'
    _rec_name = 'document'

    line_id = fields.Integer(string='Line ID', readonly=True)
    res_id = fields.Integer(string='Document ID', readonly=True)
    res_model = fields.Char(string='Model', readonly=True)
    document = fields.Char(string='Document', readonly=True)
    operation_type = fields.Selection([
        ('order', 'Vente'),
        ('purchase', 'Achat'),
        ('transfer', 'Transfert'),
    ], string="Type d'opération", readonly=True)
    movement_type = fields.Selection([
        ('delivery', 'Livraison'),
        ('receipt', 'Réception'),
        ('transfer_out', 'Transfert sortant'),
        ('transfer_in', 'Transfert entrant'),
    ], string="Type de mouvement", readonly=True)
    date = fields.Date(string='Date', readonly=True)
    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', readonly=True)
    stock_source_id = fields.Many2one('sm_stocks.stock', string='Stock source', readonly=True)
    stock_dest_id = fields.Many2one('sm_stocks.stock', string='Stock destination', readonly=True)
    product_id = fields.Many2one('sm_sales.product', string='Article', readonly=True)
    product_code = fields.Char(string='Réf.', related='product_id.code', readonly=True)
    partner_id = fields.Many2one('sm_sales.partner', string='Client/Fournis.', readonly=True)
    stock_state = fields.Selection([
        ('pending', 'En attente'),
        ('received', 'Reçu'),
        ('delivered', 'Livré'),
        ('returned', 'Retourné'),
    ], string='État', readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('canceled', 'Annulé'),
    ], string='État document', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsable', readonly=True)
    company_id = fields.Many2one('res.company', string='Société', readonly=True)
    order_line_name = fields.Char(string='Description ligne', readonly=True)
    name = fields.Char(string='Désignation', compute='_compute_name', search='_search_name')
    qty = fields.Float(string='Quantité', readonly=True, digits='Quantity')
    qty_value = fields.Float(string='Qté Valeur', readonly=True, digits='Quantity')

    @api.depends('res_model', 'movement_type', 'order_line_name', 'stock_source_id', 'stock_dest_id')
    def _compute_name(self):
        for rec in self:
            if rec.res_model == 'sm_stocks.transfer':
                if rec.movement_type == 'transfer_out':
                    dest_name = rec.stock_dest_id.name or ''
                    rec.name = _('Transfert vers : %s') % dest_name
                elif rec.movement_type == 'transfer_in':
                    src_name = rec.stock_source_id.name or ''
                    rec.name = _('Transfert de : %s') % src_name
                else:
                    rec.name = _('Transfert')
            else:
                rec.name = rec.order_line_name or ''

    def _search_name(self, operator, value):
        return ['|', ('order_line_name', operator, value), ('document', operator, value)]

    def action_open_movement(self):
        self.ensure_one()
        if self.res_model == 'sm_sales.order':
            if self.operation_type == 'order':
                view_id = self.env.ref('sm_stocks.sm_stocks_delivery_form', raise_if_not_found=False)
                view_id = view_id.id if view_id else False
                name = _('Livraison')
            else:
                view_id = self.env.ref('sm_stocks.sm_stocks_receipt_form', raise_if_not_found=False)
                view_id = view_id.id if view_id else False
                name = _('Réception')
            return {
                'type': 'ir.actions.act_window',
                'name': name,
                'res_model': 'sm_sales.order',
                'res_id': self.res_id,
                'view_mode': 'form',
                'views': [(view_id, 'form')] if view_id else False,
                'view_id': view_id,
                'target': 'current',
            }
        elif self.res_model == 'sm_stocks.transfer':
            view_id = self.env.ref('sm_stocks.sm_stocks_transfer_form', raise_if_not_found=False)
            view_id = view_id.id if view_id else False
            return {
                'type': 'ir.actions.act_window',
                'name': _('Transfert entre stocks'),
                'res_model': 'sm_stocks.transfer',
                'res_id': self.res_id,
                'view_mode': 'form',
                'views': [(view_id, 'form')] if view_id else False,
                'view_id': view_id,
                'target': 'current',
            }
        return False

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    sol.id * 10 + 1 AS id,
                    sol.id AS line_id,
                    so.id AS res_id,
                    'sm_sales.order'::varchar AS res_model,
                    so.name AS document,
                    so.operation_type AS operation_type,
                    CASE 
                        WHEN so.operation_type = 'order' THEN 'delivery'
                        WHEN so.operation_type = 'purchase' THEN 'receipt'
                        ELSE 'delivery'
                    END AS movement_type,
                    COALESCE(sol.date, so.date) AS date,
                    COALESCE(sol.stock_id, so.stock_id) AS stock_id,
                    COALESCE(sol.stock_id, so.stock_id) AS stock_source_id,
                    NULL::integer AS stock_dest_id,
                    sol.product_id AS product_id,
                    sol.partner_id AS partner_id,
                    so.stock_state AS stock_state,
                    so.state AS state,
                    sol.user_id AS user_id,
                    sol.company_id AS company_id,
                    sol.name AS order_line_name,
                    sol.qty AS qty,
                    sol.qty_value AS qty_value
                FROM sm_sales_order_line sol
                JOIN sm_sales_order so ON sol.order_id = so.id
                WHERE COALESCE(sol.stock_id, so.stock_id) IS NOT NULL

                UNION ALL

                SELECT
                    stl.id * 10 + 2 AS id,
                    stl.id AS line_id,
                    st.id AS res_id,
                    'sm_stocks.transfer'::varchar AS res_model,
                    st.name AS document,
                    'transfer'::varchar AS operation_type,
                    'transfer_out'::varchar AS movement_type,
                    COALESCE(stl.date, st.date) AS date,
                    COALESCE(stl.stock_source_id, st.stock_source_id) AS stock_id,
                    COALESCE(stl.stock_source_id, st.stock_source_id) AS stock_source_id,
                    COALESCE(stl.stock_dest_id, st.stock_dest_id) AS stock_dest_id,
                    stl.product_id AS product_id,
                    NULL::integer AS partner_id,
                    CASE
                        WHEN st.state = 'done' THEN 'delivered'
                        WHEN st.state = 'cancel' THEN 'returned'
                        ELSE 'pending'
                    END AS stock_state,
                    CASE
                        WHEN st.state = 'done' THEN 'confirmed'
                        WHEN st.state = 'cancel' THEN 'canceled'
                        ELSE 'draft'
                    END AS state,
                    st.user_id AS user_id,
                    st.company_id AS company_id,
                    NULL::varchar AS order_line_name,
                    stl.qty AS qty,
                    -stl.qty AS qty_value
                FROM sm_stocks_transfer_line stl
                JOIN sm_stocks_transfer st ON stl.transfer_id = st.id

                UNION ALL

                SELECT
                    stl.id * 10 + 3 AS id,
                    stl.id AS line_id,
                    st.id AS res_id,
                    'sm_stocks.transfer'::varchar AS res_model,
                    st.name AS document,
                    'transfer'::varchar AS operation_type,
                    'transfer_in'::varchar AS movement_type,
                    COALESCE(stl.date, st.date) AS date,
                    COALESCE(stl.stock_dest_id, st.stock_dest_id) AS stock_id,
                    COALESCE(stl.stock_source_id, st.stock_source_id) AS stock_source_id,
                    COALESCE(stl.stock_dest_id, st.stock_dest_id) AS stock_dest_id,
                    stl.product_id AS product_id,
                    NULL::integer AS partner_id,
                    CASE
                        WHEN st.state = 'done' THEN 'received'
                        WHEN st.state = 'cancel' THEN 'returned'
                        ELSE 'pending'
                    END AS stock_state,
                    CASE
                        WHEN st.state = 'done' THEN 'confirmed'
                        WHEN st.state = 'cancel' THEN 'canceled'
                        ELSE 'draft'
                    END AS state,
                    st.user_id AS user_id,
                    st.company_id AS company_id,
                    NULL::varchar AS order_line_name,
                    stl.qty AS qty,
                    stl.qty AS qty_value
                FROM sm_stocks_transfer_line stl
                JOIN sm_stocks_transfer st ON stl.transfer_id = st.id
            )
        """ % self._table)
