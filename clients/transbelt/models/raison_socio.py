from odoo import models, fields, api

class RaisonSocioModule(models.Model):
    _name = 'albelt.raison_socio'
    _description = 'Raisons social'

    name = fields.Char( string='name', required=True  )

    _check_name_raison_uniq = models.Constraint(
        'UNIQUE(name)',
        'Le Nom doit être unique !',
    )
   