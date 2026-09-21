# -*- coding: utf-8 -*-

from odoo import models, fields

class SmBoxesBoxes(models.Model):
    _name = 'sm_boxes.boxes'
    _description = 'Caisses et comptes financiers'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Compte",  required=True, translate=True, index=True, tracking=1)
    active = fields.Boolean(string='Actif', default=True)

    company_id = fields.Many2one('res.company', 'Société', default=lambda self: self.env.company, index=True)
    boxe_type = fields.Selection(string="Type", selection=[  ('bank',  'Banque'),  ('sold',  'Espèce') ], required=True,default='sold', tracking=2) 

    user_ids = fields.Many2many(comodel_name="res.users", string="Responsables", )

    rib = fields.Char(string="RIB", required=False, )
    bank_id = fields.Many2one("sm_sales.bank")

    operations_ids= fields.One2many('sm_boxes.operations','boxe_id')

    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Le nom de compte doit être unique. Veuillez choisir un autre nom.',
    )
   



