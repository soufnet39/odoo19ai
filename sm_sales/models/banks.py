from odoo import models, fields

class MyBanks(models.Model):
    _name='sm_sales.bank'
    _description = 'banks'
    _rec_name = 'name'
    _order = 'sequence, name'

    sequence = fields.Integer(string="Séquence", default=10)
    name = fields.Char(string="Nom", required=True, )
    reference = fields.Char(string="Référence"  )