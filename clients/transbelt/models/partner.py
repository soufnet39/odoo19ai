from odoo import models, fields , api

class AlbeltPartner(models.Model):
    _inherit = 'sm_sales.partner'

        
    name = fields.Char(index=True, string="Nom société", required=True)
   
    industry_id = fields.Many2one(
        string='Industrie',
        comodel_name='albelt.industry',
        ondelete='restrict',
    )
 
    raison_social_id = fields.Many2one(
        string='Raison Social',
        comodel_name='albelt.raison_socio',
        ondelete='restrict',
    )
   
           
   