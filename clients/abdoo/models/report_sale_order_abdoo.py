# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class ReportSaleOrderAbdoo(models.AbstractModel):
    _name = 'report.abdoo.report_saleorder_abdoo'
    _description = 'Rapport Commande Vente Étroit (10cm)'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sm_sales.order'].browse(docids)
        for doc in docs:
            if doc.operation_type != 'order':
                raise UserError(
                    _("Le document '%s' n'est pas une commande de vente. "
                      "Ce rapport étroit est réservé exclusivement aux commandes de vente (pas aux achats).") % (doc.name or '')
                )
        return {
            'doc_ids': docids,
            'doc_model': 'sm_sales.order',
            'docs': docs,
            'data': data,
        }
