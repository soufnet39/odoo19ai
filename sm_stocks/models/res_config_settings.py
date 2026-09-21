# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # General Settings

    delivery_confirmed_by_default = fields.Boolean(
        "La livraison automatique à la commande",
        config_parameter='sm_stocks.delivery_confirmed_by_default',
        
    )
    reception_confirmed_by_default = fields.Boolean(
        "La Réception automatique à l'achat",
        config_parameter='sm_stocks.reception_confirmed_by_default',
         
    )
   
   