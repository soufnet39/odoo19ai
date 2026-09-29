# -*- coding: utf-8 -*-
from odoo import models, fields


class Zones(models.Model):
    _name = 'abdoo.zones'
    _description = 'Zone'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    active = fields.Boolean(string='Actif', default=True)
