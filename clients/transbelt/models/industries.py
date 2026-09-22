from odoo import models, fields, api

class IndustrieAlbelt(models.Model):
    _name = 'albelt.industry'
    _description = 'Industrie'

    name = fields.Char( string='name', required=True  )
    fullname = fields.Char(string='Full Name')
    archive = fields.Boolean(string='Archivé', default=False)

    _check_name_industryname_uniq = models.Constraint(
        'UNIQUE(name)',
        'Le Nom doit être unique !',
    )
   
