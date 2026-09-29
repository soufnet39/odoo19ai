# -*- coding: utf-8 -*-
from odoo import models, fields


class Motors(models.Model):
    _name = 'motors'
    _description = 'Moteur'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
    )
