from odoo import models, fields 

class AlbeltPartner(models.Model):
    _inherit = 'sm_sales.quotation'

    show_griff = fields.Boolean(string="Afficher le cachet", default=False)