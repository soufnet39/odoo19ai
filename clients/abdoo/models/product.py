# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.fields import Domain


class ProductTemplate(models.Model):
    _inherit = 'sm_sales.product'

    reference_filter = fields.Char(
        string='Ref. Filtre',
    )

    maison = fields.Many2many(
        'abdoo.maison.marques',
        string='Maison',
    )

    zone = fields.Many2one(
        'abdoo.zones',
        string='Zone',
        related='maison.zone',
        store=True,
    )

    age = fields.Selection(
        selection=[
            ('A', 'Ancien'),
            ('N', 'Nouveau'),
        ],
        string='Age',
    )

    carburant = fields.Selection(
        selection=[
            ('E', 'Essence'),
            ('D', 'Diesel'),
        ],
        string='Nature carburant',
    )

    moteur = fields.Many2one(
        'abdoo.motors',
        string='Moteur',
    )

    moteur_type = fields.Many2one(
        'abdoo.motor.types',
        string='Type Moteur',
    )

    filter_marque = fields.Many2one(
        'abdoo.filter.marques',
        string='Marque de Filtre',
    )

    filter_type = fields.Selection(
        selection=[
            ('clim', 'Clim'),
            ('gazoil', 'Gazoil'),
            ('air', 'A air'),
            ('essence', 'Essence'),
            ('huile', 'A huile'),
        ],
        string='Type de filtre',
    )

   
    # -------------------------------------------------------
    # Custom display_name
    # -------------------------------------------------------
    display_name = fields.Char(
        string='Nom affiché',
        compute='_compute_display_name',
        store=True,
        index=True,
    )

    @api.depends('name', 'reference_filter', 'filter_marque.name', 'filter_type', 'age', 'carburant', 'moteur.name', 'moteur_type.name', 'code')
    def _compute_display_name(self):
        filter_type_labels = dict(self._fields['filter_type'].selection)
        age_labels = dict(self._fields['age'].selection)
        carburant_labels = dict(self._fields['carburant'].selection)

        for rec in self:
            parts = [rec.name or '']
            if rec.reference_filter:
                parts.append(rec.reference_filter)
            if rec.filter_marque:
                parts.append(rec.filter_marque.name)
            if rec.filter_type:
                parts.append(filter_type_labels.get(rec.filter_type, rec.filter_type))
            if rec.age:
                parts.append(age_labels.get(rec.age, rec.age))
            if rec.carburant:
                parts.append(carburant_labels.get(rec.carburant, rec.carburant))
            if rec.moteur:
                parts.append(rec.moteur.name)
            if rec.moteur_type:
                parts.append(rec.moteur_type.name)
            if rec.code:
                parts.append(rec.code)
            rec.display_name = ', '.join(filter(None, parts))

    def action_print_listing(self, visible_columns=None):
        default = ['maison', 'display_name', 'code', 'zone',
                   'reference_filter', 'filter_marque', 'default_price']
        return self.env.ref('abdoo.action_report_product_listing').report_action(
            self, data={'visible_columns': visible_columns or default}
        )

    # -------------------------------------------------------
    # Custom Search (multi-word AND search on display_name)
    # -------------------------------------------------------
    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100, **kwargs):
        if name and operator in ('ilike', 'like', '=ilike', '=like'):
            words = name.split()
            if words:
                name_domain = Domain.AND([Domain('display_name', 'ilike', word) for word in words])
                full_domain = name_domain & Domain(domain or Domain.TRUE)
                records = self.search_fetch(full_domain, ['display_name'], limit=limit)
                return [(record.id, record.display_name) for record in records.sudo()]
        return super().name_search(name=name, domain=domain, operator=operator, limit=limit, **kwargs)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, **kwargs):
        domain = Domain(domain)

        def _split_conditions(c):
            if (
                c.field_expr in ('display_name', 'name')
                and c.operator in ('ilike', 'like', '=ilike', '=like')
                and isinstance(c.value, str)
            ):
                words = c.value.split()
                if len(words) > 1:
                    return Domain.AND([Domain('display_name', 'ilike', word) for word in words])
            return c

        domain = domain.map_conditions(_split_conditions)
        return super()._search(domain, offset=offset, limit=limit, order=order, **kwargs)
