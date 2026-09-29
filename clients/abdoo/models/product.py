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
        'motors',
        string='Moteur',
    )

    moteur_type = fields.Many2one(
        'motor.types',
        string='Type Moteur',
    )

    filter_marque = fields.Many2one(
        'filter.marques',
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

   

    _rec_names_search = ['name', 'code']

    # -------------------------------------------------------
    # Custom display_name
    # -------------------------------------------------------
    display_name = fields.Char(
        string='Nom affiché',
        compute='_compute_display_name',
        store=True,
    )

    @api.depends('name', 'filter_marque.name', 'filter_type', 'age', 'carburant', 'moteur.name', 'moteur_type.name', 'code')
    def _compute_display_name(self):
        filter_type_labels = dict(self._fields['filter_type'].selection)
        age_labels = dict(self._fields['age'].selection)
        carburant_labels = dict(self._fields['carburant'].selection)

        for rec in self:
            parts = [rec.name or '']           
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

    def _search_display_name(self, operator, value):
        """Extend display_name search to cover all fields that compose it.
        When the search phrase contains spaces, each word is required to appear
        in display_name (AND logic). Example: "1.5 dci" → display_name contains
        "1.5" AND display_name contains "dci".
        """
        positive_ops = ('ilike', 'like', '=', '=ilike', '=like')

        # Multi-word AND search: split on spaces and require every chunk to match
        if value and operator in positive_ops and isinstance(value, str) and ' ' in value:
            chunks = value.split()
            combined = Domain.TRUE
            for chunk in chunks:
                combined = combined & Domain(self._search_display_name(operator, chunk))
            return combined

        # Use name and code directly as the base domain instead of super()
        # to avoid infinite recursion since sm_sales.product has _rec_name = 'display_name'
        domain = Domain(['|', ('name', operator, value), ('code', operator, value)])
        if value and operator in positive_ops:
            # Char: direct search
            domain = domain | Domain('reference_filter', operator, value)

            # Many2one / Many2many: search by related record name
            domain = domain | Domain('filter_marque.name', operator, value) \
                            | Domain('moteur.name', operator, value) \
                            | Domain('moteur_type.name', operator, value) \
                            | Domain('maison.name', operator, value) \
                            | Domain('maison.zone.name', operator, value)

            # Selection: match against human-readable labels
            val_lower = value.lower()
            for sel_field in ('filter_type', 'age', 'carburant'):
                labels = dict(self._fields[sel_field].selection)
                if operator in ('ilike', '=ilike'):
                    keys = [k for k, v in labels.items() if val_lower in v.lower()]
                elif operator in ('like', '=like'):
                    keys = [k for k, v in labels.items() if value in v]
                else:  # '='
                    keys = [k for k, v in labels.items() if v == value]
                if keys:
                    domain = domain | Domain(sel_field, 'in', keys)
        return domain


# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     @api.depends('product_tmpl_id.display_name')
#     def _compute_display_name(self):
#         for product in self:
#             product.display_name = product.product_tmpl_id.display_name or product.name

#     def name_search(self, name='', domain=None, operator='ilike', limit=100):
#         """Extend product.product search to include abdoo extra fields."""
#         results = super().name_search(name, domain, operator, limit)
#         positive_ops = ('ilike', 'like', '=', '=ilike', '=like')
#         if name and operator in positive_ops:
#             existing_ids = {r[0] for r in results}
#             base_domain = Domain(domain or Domain.TRUE)

#             # Build AND domain across space-separated chunks
#             if isinstance(name, str) and ' ' in name:
#                 chunks = name.split()
#                 name_domain = Domain.TRUE
#                 for chunk in chunks:
#                     name_domain = name_domain & Domain('display_name', operator, chunk)
#             else:
#                 name_domain = Domain('display_name', operator, name)

#             extra = self.search_fetch(
#                 base_domain & name_domain,
#                 ['display_name'],
#                 limit=limit,
#             )
#             extra_pairs = [(p.id, p.display_name) for p in extra if p.id not in existing_ids]
#             results = (results + extra_pairs)[:limit] if limit else results + extra_pairs
#         return results

#     def _search_display_name(self, operator, value):
#         """Mirror ProductTemplate._search_display_name for product.product searches.

#         When the search phrase contains spaces, each word is required to appear
#         in display_name (AND logic).
#         """
#         positive_ops = ('ilike', 'like', '=', '=ilike', '=like')

#         # Multi-word AND search: split on spaces and require every chunk to match
#         if value and operator in positive_ops and isinstance(value, str) and ' ' in value:
#             chunks = value.split()
#             combined = Domain.TRUE
#             for chunk in chunks:
#                 combined = combined & Domain(self._search_display_name(operator, chunk))
#             return combined

#         domain = Domain(super()._search_display_name(operator, value))
#         if value and operator in positive_ops:
#             domain = domain | Domain('product_tmpl_id.reference_filter', operator, value)

#             domain = domain | Domain('filter_marque.display_name', operator, value) \
#                             | Domain('moteur.display_name', operator, value) \
#                             | Domain('moteur_type.display_name', operator, value) \
#                             | Domain('product_tmpl_id.maison.zone.name', operator, value)

#             val_lower = value.lower()
#             for sel_field in ('filter_type', 'age', 'carburant'):
#                 labels = dict(self.env['product.template']._fields[sel_field].selection)
#                 if operator in ('ilike', '=ilike'):
#                     keys = [k for k, v in labels.items() if val_lower in v.lower()]
#                 elif operator in ('like', '=like'):
#                     keys = [k for k, v in labels.items() if value in v]
#                 else:  # '='
#                     keys = [k for k, v in labels.items() if v == value]
#                 if keys:
#                     domain = domain | Domain(sel_field, 'in', keys)
#         return domain
