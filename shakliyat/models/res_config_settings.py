# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hide_discuss = fields.Boolean(
        string='Masquer Discussions',
        config_parameter='shakliyat.hide_discuss',
        default=False,
        help="Lorsque cette option est activée, l'application Discussions et tous ses menus sont masqués dans l'interface.",
    )

    dark_mode = fields.Boolean(
        string='Mode sombre',
        config_parameter='shakliyat.dark_mode',
        default=False,
        help="Lorsque cette option est activée, l'interface d'administration adopte une palette de couleurs sombres.",
    )
