# -*- coding: utf-8 -*-
from odoo import fields, models


class SmBoxesOperations(models.Model):
    _inherit = 'sm_boxes.operations'

    session_id = fields.Many2one('sm_pos.session', string='Session du point de vente', index=True, copy=False)
    payment_mode_id = fields.Many2one('me_sales.payment.mode', string='Mode de paiement', copy=False)