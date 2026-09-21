from odoo import models, fields, api

class SMSalesProductCategory(models.Model):
    _name = 'sm_sales.product.category'
    _description = 'Catégorie de produits commerciaux'
    _order = 'name'

    name = fields.Char(string='Nom', required=True, index=True)
    product_ids = fields.One2many('sm_sales.product', 'categ_id', string='Produits')
    product_count = fields.Integer(string='Nombre de produits', compute='_compute_product_count')

    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)