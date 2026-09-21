# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettingsBoxes(models.TransientModel):
    _inherit = 'res.config.settings'

    # General Settings
    show_client_payment = fields.Boolean(
        string='Afficher les paiements des clients',
        config_parameter='sm_boxes.show_client_payment',
    )
    show_supplier_payment = fields.Boolean(
        string='Afficher les réglements des fournisseurs',
        config_parameter='sm_boxes.show_supplier_payment',
    )