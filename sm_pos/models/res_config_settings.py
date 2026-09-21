# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_default_stock_id = fields.Many2one(
        'sm_stocks.stock', string='Stock par défaut',
        config_parameter='sm_pos.default_stock_id',
    )
    pos_default_pricelist_id = fields.Many2one(
        'sm_sales.pricelist', string='Liste de prix par défaut',
        config_parameter='sm_pos.default_pricelist_id',
    )
    pos_default_boxe_id = fields.Many2one(
        'sm_boxes.boxes', string='Caisse par défaut',
        config_parameter='sm_pos.default_boxe_id',
    )
    pos_receipt_show_tva = fields.Boolean(
        string='Afficher la TVA sur le reçu',
        config_parameter='sm_pos.receipt_show_tva',
        default=True,
    )