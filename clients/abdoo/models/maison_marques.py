# -*- coding: utf-8 -*-
from odoo import models, fields


class MaisonMarques(models.Model):
    _name = 'abdoo.maison.marques'
    _description = 'Marque Maison'
    _order = 'name'
    _sql_constraints = [
        ('name_unique_ci', 'UNIQUE(LOWER(name))', 'Ce nom de marque existe déjà.'),
    ]

    name = fields.Char(
        string='Nom',
        required=True,
    )

    zone = fields.Many2one(
        comodel_name='abdoo.zones',
        string='Zone',
        ondelete='set null',
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
    )
