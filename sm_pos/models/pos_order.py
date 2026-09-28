# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SmSalesOrder(models.Model):
    _inherit = 'sm_sales.order'

    session_id = fields.Many2one('sm_pos.session', string='Session du point de vente', index=True, copy=False)
    pos_config_id = fields.Many2one('sm_pos.config', string='Point de vente', index=True, copy=False)
    is_pos_order = fields.Boolean(string='Commande du point de vente', default=False, copy=False, index=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_pos_order'):
                current_name = vals.get('name')
                if not current_name or current_name in ('<new order>', '_< Nouveau >_'):
                    vals['name'] = self.env['ir.sequence'].next_by_code('sm_sales.order.pos') or '/'
        return super().create(vals_list)

    def action_view_session(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Session du point de vente'),
            'res_model': 'sm_pos.session',
            'view_mode': 'form',
            'res_id': self.session_id.id,
        }