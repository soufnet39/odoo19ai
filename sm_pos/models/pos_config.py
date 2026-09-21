# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SmPosConfig(models.Model):
    _name = 'sm_pos.config'
    _description = 'Configuration du point de vente'
    _order = 'name'

    name = fields.Char(string='Point de vente', required=True, index=True)
    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company, index=True)
    active = fields.Boolean(default=True)

    stock_id = fields.Many2one('sm_stocks.stock', string='Stock', required=True,
                               default=lambda self: self._default_stock_id(),
                               help='Stock utilisé pour les livraisons du point de vente.')
    pricelist_id = fields.Many2one('sm_sales.pricelist', string='Liste de prix',
                                   default=lambda self: self._default_pricelist_id(),
                                   help='Liste de prix par défaut appliquée aux commandes du point de vente.')
    boxe_id = fields.Many2one('sm_boxes.boxes', string='Caisse',
                              default=lambda self: self._default_boxe_id(),
                              help='Caisse utilisée pour enregistrer les paiements du point de vente.')
    payment_mode_ids = fields.Many2many('me_sales.payment.mode', string='Modes de paiement',
                                        help='Modes de paiement disponibles dans ce point de vente.')
    user_ids = fields.Many2many('res.users', string='Caissiers',
                                help='Utilisateurs autorisés à utiliser ce point de vente. Si vide, tous les utilisateurs peuvent l’utiliser.')

    session_ids = fields.One2many('sm_pos.session', 'config_id', string='Sessions')
    current_session_id = fields.Many2one('sm_pos.session', string='Session actuelle',
                                         compute='_compute_current_session')

    @api.model
    def _default_stock_id(self):
        param = self.env['ir.config_parameter'].sudo().get_param('sm_pos.default_stock_id')
        return param and int(param) or False

    @api.model
    def _default_pricelist_id(self):
        param = self.env['ir.config_parameter'].sudo().get_param('sm_pos.default_pricelist_id')
        return param and int(param) or False

    @api.model
    def _default_boxe_id(self):
        param = self.env['ir.config_parameter'].sudo().get_param('sm_pos.default_boxe_id')
        return param and int(param) or False

    @api.depends('session_ids.state')
    def _compute_current_session(self):
        for config in self:
            config.current_session_id = config.session_ids.filtered(
                lambda s: s.state in ('opening_control', 'opened', 'closing_control')
            )[:1]