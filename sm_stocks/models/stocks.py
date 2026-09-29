# -*- coding: utf-8 -*-
import ast
from odoo import api, fields, models, _

class SmStocksStocks(models.Model):
    _name = "sm_stocks.stock"
    _description = "Mizan Stocks"
    _order = 'name'


    name = fields.Char('Name', index=True, required=True, translate=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, index=True)

    can_be_negatif = fields.Boolean(string="Stock negatif", default=False  )
    nature = fields.Selection(string="Nature",
                              selection=[
                                         ('fix', 'Fixe'),
                                         ('mobil', 'Mobile'),
                                         ('virtual', 'Virtuel'),
                                         ], required=True, default='fix')


    user_ids = fields.Many2many( "res.users", string= "Résponsables", )

    wilaya_id = fields.Many2one("sm_base.wilayates", string='Wilaya', required=True )
    description=fields.Char(string='Description')

    movement_count = fields.Integer(
        string="Nombre de mouvements",
        compute='_compute_movement_count',
    )
    transfer_count = fields.Integer(
        string="Nombre de transferts",
        compute='_compute_transfer_count',
    )

    _check_name_unique = models.Constraint(
            'UNIQUE(name)',
            'Le nom du stock doit être unique. Veuillez choisir un autre nom.',
        )

    def _compute_movement_count(self):
        for stock in self:
            if stock.id and isinstance(stock.id, int):
                stock.movement_count = self.env['sm_stocks.stock.movement'].search_count([('stock_id', '=', stock.id)])
            else:
                stock.movement_count = 0

    def _compute_transfer_count(self):
        for stock in self:
            if stock.id and isinstance(stock.id, int):
                stock.transfer_count = self.env['sm_stocks.transfer'].search_count([
                    '|',
                    ('stock_source_id', '=', stock.id),
                    ('stock_dest_id', '=', stock.id),
                ])
            else:
                stock.transfer_count = 0

    def action_view_transfers(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('sm_stocks.sm_stocks_transfer_action')
        action['domain'] = ['|', ('stock_source_id', '=', self.id), ('stock_dest_id', '=', self.id)]
        ctx = ast.literal_eval(action['context']) if isinstance(action.get('context'), str) else dict(action.get('context') or {})
        ctx.update({
            'default_stock_source_id': self.id,
        })
        action['context'] = ctx
        return action

    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('sm_stocks.sm_stocks_stock_movement_action')
        action['domain'] = [('stock_id', '=', self.id)]
        ctx = ast.literal_eval(action['context']) if isinstance(action.get('context'), str) else dict(action.get('context') or {})
        ctx.update({
            'default_stock_id': self.id,
            'search_default_stock_id': self.id,
        })
        action['context'] = ctx
        list_view = self.env.ref('sm_stocks.sm_stocks_stock_movement_list', raise_if_not_found=False)
        if list_view:
            action['views'] = [(list_view.id, 'list')]
        return action

    action_view_operations = action_view_stock_moves
