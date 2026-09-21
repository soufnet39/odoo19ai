# -*- coding: utf-8 -*-
from odoo import  models, fields

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

    _check_name_unique = models.Constraint(
            'UNIQUE(name)',
            'Le nom du stock doit être unique. Veuillez choisir un autre nom.',
        )
