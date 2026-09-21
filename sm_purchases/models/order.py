from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool

class SmPurchasesPurchase(models.Model):
    _inherit = "sm_sales.order"

   
    ref_facture_achat_source = fields.Char(string="Num. Réference"    )
    
    can_change_product_designation_on_purchases = fields.Boolean(string="Modifier la désignation", store=False,
                                default=lambda self: str2bool(self.env['ir.config_parameter'].sudo().get_param('sm_purchases.can_change_product_designation_on_purchases', 'False')))
               
    def print_purchase(self):
        return self.env.ref('sm_purchases.action_report_purchase').report_action(self)

    # TODO : redéfinir les champs avec les valeurs par défaut des paramètres, comme tva_enabled, discount, etc.
   
   
    
# ########################################################################################################################
# ########################################################################################################################
# ########################################################################################################################

class SmSalePurchaseLine(models.Model):
    _inherit = 'sm_sales.order.line'

  
    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(SmSalePurchaseLine, self)._onchange_product_id()
        if self.product_id and self.order_id.operation_type == 'purchase':
            self.name = self.product_id.name
            self.unit_price = self.product_id.purchase_price

    code_supplier = fields.Char(string="Réf.Fourn.", related='product_id.code_supplier')
   