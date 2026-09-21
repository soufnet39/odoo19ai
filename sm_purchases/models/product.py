from odoo import models, fields


class SmPurchaseProduct(models.Model):
    _inherit = "sm_sales.product"

    purchase_ok = fields.Boolean('Peut être acheté', default=True)
    code_supplier = fields.Char(string='Ref. Fourn.', index=True)
    purchase_price = fields.Float(string='Prix d\'achat', digits='Product Price', groups='base.group_user')

