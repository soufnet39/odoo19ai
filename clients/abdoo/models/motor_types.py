# -*- coding: utf-8 -*-
from odoo import models, fields


class MotorTypes(models.Model):
    _name = 'abdoo.motor.types'
    _description = 'Type Moteur'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
    )
