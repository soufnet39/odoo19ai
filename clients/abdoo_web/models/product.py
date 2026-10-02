# -*- coding: utf-8 -*-
from odoo import models, fields


class SMSalesProduct(models.Model):
    _inherit = 'sm_sales.product'

    is_published = fields.Boolean(
        string='Publié',
        default=False,
        copy=False,
        help="Indique si le produit est publié sur le web.",
    )
