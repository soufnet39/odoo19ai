# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SMSalesPartner(models.Model):
    _name = 'sm_sales.partner'
    _description = 'Partenaire commercial'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _order = 'name'

    name = fields.Char(string='Nom', required=True, index=True)
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    ref = fields.Char(string='Code', index=True)
    active = fields.Boolean(default=True)
    is_customer = fields.Boolean(string='Est un client', default=False, index=True)
    is_supplier = fields.Boolean(string='Est un fournisseur', default=False, index=True)
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company, index=True)

    # Coordonnées
    address = fields.Char(string='Adresse')
    city = fields.Char(string='Ville')
    email = fields.Char(string='E-mail')
    phone = fields.Char(string='Téléphone')
    mobile = fields.Char(string='Mobile')
    website = fields.Char(string='Site web')

    # Informations commerciales
    wilaya_id = fields.Many2one('sm_base.wilayates', string='Wilaya', ondelete='restrict', index=True)
    user_ids = fields.Many2many('res.users', string='Commerciaux')

    # Informations fiscales
    reg_com = fields.Char(string='Reg. Com.')
    art_imp = fields.Char(string='Art. Imp.')
    nif = fields.Char(string='N.I.F.')
    nis = fields.Char(string='N.I.S.')

    # Enregistrements associés
    contact_ids = fields.One2many('sm_sales.partner.contact', 'partner_id', string='Contacts')
    note = fields.Text(string='Notes')
    image_512 = fields.Image(string='Image', max_width=512, max_height=512, store=True)

    # Compteurs calculés
    # proforma_count = fields.Integer(string='Nombre de proformas', compute='_compute_proforma_count', store=True)
    # order_count = fields.Integer(string='Nombre de commandes', compute='_compute_order_count')

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name

    # @api.depends('proforma_ids')
    # def _compute_proforma_count(self):
    #     for record in self:
    #         record.proforma_count = self.env['sm_sales.proforma'].search_count([
    #             ('partner_id', '=', record.id)
    #         ])

    # def _compute_order_count(self):
    #     for record in self:
    #         record.order_count = self.env['sm_sales.sale.order'].search_count([
    #             ('partner_id', '=', record.id)
    #         ])

    def action_view_proformas(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Proformas'),
            'res_model': 'sm_sales.proforma',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_view_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes de vente'),
            'res_model': 'sm_sales.sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }


class MeSalesPartnerContact(models.Model):
    _name = 'sm_sales.partner.contact'
    _description = 'Contact du partenaire'
    _order = 'name'

    name = fields.Char(string='Nom', required=True)
    function = fields.Char(string='Fonction')
    phone = fields.Char(string='Téléphone')
    email = fields.Char(string='E-mail')
    partner_id = fields.Many2one('sm_sales.partner', string='Partenaire', required=True, ondelete='cascade', index=True)






