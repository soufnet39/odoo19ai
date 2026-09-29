# -*- coding: utf-8 -*-
from odoo import models, fields


class FilterMarques(models.Model):
    _name = 'filter.marques'
    _description = 'Marque de Filtre'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
    )
