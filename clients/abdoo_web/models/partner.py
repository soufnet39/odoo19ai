# -*- coding: utf-8 -*-
from odoo import models, fields


class SMSalesPartner(models.Model):
    _inherit = 'sm_sales.partner'

    can_view_catalog_prices = fields.Boolean(
        string='Voir les prix du catalogue web',
        default=False,
        help="Si coché, ce client est autorisé à visualiser les prix sur le catalogue web.",
    )
