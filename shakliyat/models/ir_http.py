# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result['hide_discuss'] = bool(
            self.env['ir.config_parameter'].sudo().get_param('shakliyat.hide_discuss')
        )
        result['dark_mode'] = bool(
            self.env['ir.config_parameter'].sudo().get_param('shakliyat.dark_mode')
        )
        return result
