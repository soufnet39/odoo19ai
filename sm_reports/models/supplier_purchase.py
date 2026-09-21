# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SupplierPurchaseReport(models.Model):
    _name = 'sm_reports.supplier.purchase'
    _description = 'Récapitulatif des achats fournisseurs'
    _rec_name = 'name'
    _order = 'name'

    partner_id = fields.Many2one('sm_sales.partner', string='Fournisseur', readonly=True,
                                 required=True, index=True)
    name = fields.Char(related='partner_id.name', store=True, index=True)

    date_from = fields.Date(string='Du' )
    date_to = fields.Date(string='Au' )

    purchase_count = fields.Integer(string='Nbr Achats', compute='_compute_recap')
    total_purchase = fields.Float(string='Total Achats', compute='_compute_recap',
                                  digits='Product Price')
    total_payment = fields.Float(string='Paiements', compute='_compute_recap',
                                 digits='Product Price')
    balance = fields.Float(string='Restes', compute='_compute_recap',
                           digits='Product Price', store=True)

    purchase_ids = fields.One2many('sm_sales.order', compute='_compute_purchases',
                                   string='Achats')
    payment_ids = fields.One2many('sm_boxes.operations', compute='_compute_payments',
                                  string='Paiements')

    def reset_dates(self):
        self.date_from = False
        self.date_to = False

    def _purchase_domain(self, rec):
        domain = [
            ('partner_id', '=', rec.partner_id.id),
            ('operation_type', '=', 'purchase'),
            ('state', '=', 'confirmed'),
            ('is_pos_order', '=', False),
        ]
        if rec.date_from:
            domain.append(('date', '>=', rec.date_from))
        if rec.date_to:
            domain.append(('date', '<=', rec.date_to))
        return domain

    def _payment_domain(self, rec):
        domain = [
            ('partner_id', '=', rec.partner_id.id),
            ('operation', 'in', ['achat', 'decaissement']),
        ]
        if rec.date_from:
            domain.append(('date', '>=', rec.date_from))
        if rec.date_to:
            domain.append(('date', '<=', rec.date_to))
        return domain

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_recap(self):
        for rec in self:
            purchases = self.env['sm_sales.order'].search(self._purchase_domain(rec))
            payments = self.env['sm_boxes.operations'].search(self._payment_domain(rec))
            rec.purchase_count = len(purchases)
            rec.total_purchase = sum(purchases.mapped('amount_ttc'))
            # Les paiements fournisseurs sont enregistrés au débit (amount_done négatif),
            # on les inverse donc pour afficher le montant payé au fournisseur en positif.
            rec.total_payment = -sum(payments.mapped('amount_done'))
            rec.balance = rec.total_purchase - rec.total_payment

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_purchases(self):
        for rec in self:
            rec.purchase_ids = self.env['sm_sales.order'].search(self._purchase_domain(rec))

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_payments(self):
        for rec in self:
            rec.payment_ids = self.env['sm_boxes.operations'].search(self._payment_domain(rec))

    def action_print_purchases(self):
        self.ensure_one()
        return self.env.ref('sm_reports.action_report_supplier_purchases').report_action(self)

    def action_print_payments(self):
        self.ensure_one()
        return self.env.ref('sm_reports.action_report_supplier_payments').report_action(self)

    def action_refresh(self):
        """Recrée une ligne de rapport par fournisseur (is_supplier=True)."""
        self = self.sudo()
        self.search([]).unlink()
        suppliers = self.env['sm_sales.partner'].sudo().search([('is_supplier', '=', True)])
        self.create([{'partner_id': supplier.id} for supplier in suppliers])
        return True


class SupplierPurchasePartner(models.Model):
    """Maintient les lignes du récapitulatif des achats fournisseurs synchronisées avec les fournisseurs."""
    _inherit = 'sm_sales.partner'

    def _sync_supplier_report(self):
        report = self.env['sm_reports.supplier.purchase']
        for partner in self:
            existing = report.search([('partner_id', '=', partner.id)])
            if partner.is_supplier:
                if not existing:
                    report.create({'partner_id': partner.id})
            else:
                existing.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._sync_supplier_report()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if 'is_supplier' in vals:
            self._sync_supplier_report()
        return res