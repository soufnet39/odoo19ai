
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SmInvoicesSales(models.Model):
    _inherit = "sm_sales.order"

    # ------------------------------------------------------------------
    # Lien vers les factures générées depuis cette commande.
    # Comme sm_invoices.invoice.sale_order_ids est un Many2many déclaré
    # sans paramètre `relation=`, la colonne inverse auto-générée n'est pas
    # directement accessible : on calcule donc la liste et le compteur via
    # une recherche.
    # ------------------------------------------------------------------
    invoice_ids = fields.Many2many(
        'sm_invoices.invoice',
        string='Factures',
        compute='_compute_invoice_ids',
        readonly=True,
    )
    # NOTE: non-stored on purpose. invoice_ids is non-stored too (computed
    # via search() because the M2M relation has no explicit inverse column),
    # so a stored invoice_count with @api.depends('invoice_ids') would never
    # detect changes → count stays 0 even when invoices exist. Non-stored
    # fields recompute on every read, so the count is always live.
    invoice_count = fields.Integer(
        string='Nombre de factures',
        compute='_compute_invoice_count',
        store=False,
    )

    @api.depends()
    def _compute_invoice_ids(self):
        Invoice = self.env['sm_invoices.invoice']
        for order in self:
            invoices = Invoice.search([('sale_order_ids', 'in', order.id)])
            order.invoice_ids = [(6, 0, invoices.ids)]

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for order in self:
            order.invoice_count = len(order.invoice_ids)

    # ------------------------------------------------------------------
    # Smart-button : voir les factures liées à cette commande
    # ------------------------------------------------------------------
    def action_view_invoices(self):
        self.ensure_one()
        invoice_ids = self.env['sm_invoices.invoice'].search(
            [('sale_order_ids', 'in', self.id)]
        ).ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Factures'),
            'res_model': 'sm_invoices.invoice',
            'view_mode': 'list,form',
            'domain': [('id', 'in', invoice_ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    # ------------------------------------------------------------------
    # Création d'une facture client à partir de cette commande
    # ------------------------------------------------------------------
    def action_create_invoice(self):
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError(_("Vous ne pouvez créer une facture qu'à partir d'une commande confirmée."))

        line_vals = []
        for line in self.order_lines:
            line_vals.append((0, 0, {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'name': line.name,
                'qty': line.qty,
                'unit_price': line.unit_price,
            }))

        invoice_vals = {
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'user_id': self.user_id.id,
            'tva_enabled': self.tva_enabled,
            'tva_taux': self.tva_taux,
            'remise_exist': self.remise_exist,
            'remise_methode': self.remise_methode,
            'remise_taux': self.remise_taux,
            'remise_mta': self.remise_mta,
            'mode_paiement_id': self.mode_paiement_id.id if self.mode_paiement_id else False,
            'sale_order_ids': [(4, self.id)],
            'invoice_lines': line_vals,
        }

        invoice = self.env['sm_invoices.invoice'].create(invoice_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Facture'),
            'res_model': 'sm_invoices.invoice',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
        }

