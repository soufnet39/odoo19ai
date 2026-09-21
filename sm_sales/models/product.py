# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SMSalesProduct(models.Model):
    _name = 'sm_sales.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    

    _description = 'Produits'
    _order = 'name'
    _rec_name = 'display_name'

    name = fields.Char(string='Nom', required=True, translate=True, index=True)
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    code = fields.Char(string='Référence', index=True)
    description = fields.Text(string='Description', translate=True)
    sale_ok = fields.Boolean(string='Vendable', default=True)
    default_price = fields.Float(string='Prix de vente', digits='Product Price', groups='base.group_user')
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company, index=True)
    categ_id = fields.Many2one('sm_sales.product.category', string='Catégorie', ondelete='restrict', index=True)
    product_type = fields.Selection([
        ('consu', 'Consommable'),
        ('service', 'Service'),
    ], string='Type de produit', default='consu', required=True,
        help='Un produit consommable est un produit dont le stock n’est pas géré.\n'
             'Un service est un produit immatériel que vous fournissez.')
    image_512 = fields.Image(string='Image', max_width=512, max_height=512, store=True)
    image_128 = fields.Image(string='Image 128', related='image_512', max_width=128, max_height=128, store=True)
    active = fields.Boolean(default=True)

    # Liste de prix
    use_price_list = fields.Boolean(string='Liste de prix', default=False)
    price_list_price_ids = fields.One2many(
        'sm_sales.pricelist.price', 'product_id', string='Liste des prix',
    )
    display_price = fields.Char(
        string='Prix affiché',
        compute='_compute_display_price',
    )

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name

    @api.depends('use_price_list', 'default_price',
                 'price_list_price_ids.price',
                 'price_list_price_ids.pricelist_id.name')
    def _compute_display_price(self):
        for record in self:
            if not record.use_price_list:
                record.display_price = f"{record.default_price:.2f}"
            else:
                parts = []
                for price in record.price_list_price_ids:
                    initial = (price.pricelist_id.name or '?')[:1]
                    parts.append(f"{initial}:{price.price:.2f}")
                record.display_price = ', '.join(parts)

    def copy(self, default=None):
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copie)") % self.name
        return super().copy(default=default)



