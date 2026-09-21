# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SmSalesPriceList(models.Model):
    _name = 'sm_sales.pricelist'
    _description = 'Liste de prix'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    active = fields.Boolean(default=True)
    user_ids = fields.Many2many(
        'res.users', string='Utilisateurs',
        help='Utilisateurs autorisés à utiliser cette liste de prix. Si vide, tous les utilisateurs peuvent l’utiliser.',
    )

    price_ids = fields.One2many(
        'sm_sales.pricelist.price', 'pricelist_id', string='Prix',
    )


class SmSalesPriceListPrice(models.Model):
    _name = 'sm_sales.pricelist.price'
    _description = 'Liste de prix'
    _order = 'pricelist_id, product_id'
    _rec_name = 'display_name'

    pricelist_id = fields.Many2one(
        'sm_sales.pricelist', string='Liste de prix',
        required=True, ondelete='cascade', index=True,
    )
    product_id = fields.Many2one(
        'sm_sales.product', string='Produit',
        required=True, ondelete='cascade', index=True,
    )
    price = fields.Float(
        string='Prix', required=True, digits='Product Price',
    )

    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('pricelist_id', 'price')
    def _compute_display_name(self):
        for rec in self:
            pricelist = rec.pricelist_id.name or ''
            rec.display_name = f"{pricelist}: {rec.price:.2f}"

    @api.constrains('product_id', 'pricelist_id')
    def _check_unique_product_pricelist(self):
        for rec in self:
            if not rec.product_id or not rec.pricelist_id:
                continue
            duplicate = self.search([
                ('product_id', '=', rec.product_id.id),
                ('pricelist_id', '=', rec.pricelist_id.id),
                ('id', '!=', rec.id),
            ], limit=1)
            if duplicate:
                raise ValidationError(
                    _("Chaque produit ne peut avoir qu'un seul prix par liste de prix !")
                )
