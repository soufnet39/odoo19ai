# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SMSalesOrder(models.Model):
    _inherit = 'sm_sales.order'

    def action_print_narrow_order(self):
        self.ensure_one()
        if self.operation_type != 'order':
            raise UserError(_("Ce ticket est réservé exclusivement aux commandes de vente (pas aux achats)."))
        return self.env.ref('abdoo.action_report_sale_order_abdoo').report_action(self)
