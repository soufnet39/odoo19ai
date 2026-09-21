# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CustomerSalesReport(models.Model):
    _name = 'sm_reports.customer.sales'
    _description = 'Récapitulatif des ventes clients'
    _rec_name = 'name'
    _order = 'name'

    partner_id = fields.Many2one('sm_sales.partner', string='Client', readonly=True,
                                 required=True, index=True)
    name = fields.Char(related='partner_id.name', store=True, index=True)

    date_from = fields.Date(string='Du')
    date_to = fields.Date(string='Au' )

    order_count = fields.Integer(string='Nbr Cmd.', compute='_compute_recap')
    total_sales = fields.Float(string='Ventes', compute='_compute_recap',
                               digits='Product Price')
    total_payment = fields.Float(string='Paiements', compute='_compute_recap',
                                 digits='Product Price')
    balance = fields.Float(string='Restes', compute='_compute_recap',
                           digits='Product Price' ,store=True)

    order_ids = fields.One2many('sm_sales.order', compute='_compute_orders',
                                string='Commandes')
    payment_ids = fields.One2many('sm_boxes.operations', compute='_compute_payments',
                                  string='Paiements')
    def reset_dates(self):
            self.date_from = False
            self.date_to = False

    def action_print_orders(self):
        self.ensure_one()
        return self.env.ref('sm_reports.action_report_customer_orders').report_action(self)

    def action_print_payments(self):
        self.ensure_one()
        return self.env.ref('sm_reports.action_report_customer_payments').report_action(self)

    def _order_domain(self, rec):
        domain = [
            ('partner_id', '=', rec.partner_id.id),
            ('operation_type', '=', 'order'),
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
            ('operation', 'in', ['recette', 'encaissement', 'virement', 'versement']),
            ('partner_id', '=', rec.partner_id.id),
        ]
        if rec.date_from:
            domain.append(('date', '>=', rec.date_from))
        if rec.date_to:
            domain.append(('date', '<=', rec.date_to))
        return domain

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_recap(self):
        for rec in self:
            orders = self.env['sm_sales.order'].search(self._order_domain(rec))
            payments = self.env['sm_boxes.operations'].search(self._payment_domain(rec))
            rec.order_count = len(orders)
            rec.total_sales = sum(orders.mapped('amount_ttc'))
            rec.total_payment = sum(payments.mapped('amount_done'))
            rec.balance = rec.total_sales - rec.total_payment

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_orders(self):
        for rec in self:
            rec.order_ids = self.env['sm_sales.order'].search(self._order_domain(rec))

    @api.depends('partner_id', 'date_from', 'date_to')
    def _compute_payments(self):
        for rec in self:
            rec.payment_ids = self.env['sm_boxes.operations'].search(self._payment_domain(rec))

    def action_refresh(self):
        """Recrée une ligne de rapport par client (is_customer=True)."""
        self = self.sudo()
        self.search([]).unlink()
        customers = self.env['sm_sales.partner'].sudo().search([('is_customer', '=', True)])
        self.create([{'partner_id': customer.id} for customer in customers])
        return True


class CustomerSalesPartner(models.Model):
    """Maintient les lignes du récapitulatif des ventes clients synchronisées avec les clients."""
    _inherit = 'sm_sales.partner'

    def _sync_customer_report(self):
        report = self.env['sm_reports.customer.sales']
        for partner in self:
            existing = report.search([('partner_id', '=', partner.id)])
            if partner.is_customer:
                if not existing:
                    report.create({'partner_id': partner.id})
            else:
                existing.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._sync_customer_report()
        return partners

    def write(self, vals):
        res = super().write(vals)
        if 'is_customer' in vals:
            self._sync_customer_report()
        return res