from odoo import models, fields, api

class RaisonSocioModule(models.Model):
    _name = 'albelt.raison_socio'
    _description = 'Raisons social'

    name = fields.Char( string='name', required=True  )

    _sql_constraints = [
        ('name_raison_uniq', 'unique(name)', "Le Nom doit être unique !"),
    ]
