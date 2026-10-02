# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AbdooWebPreOrder(models.Model):
    _name = 'abdoo_web.pre_order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pré-commande Web'
    _order = 'id desc, date desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True,
    )
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
    )
    partner_id = fields.Many2one(
        'sm_sales.partner',
        string='Client',
        tracking=True,
    )
    customer_name = fields.Char(
        string='Nom du client',
        required=True,
        tracking=True,
    )
    customer_email = fields.Char(
        string='Email',
        tracking=True,
    )
    customer_phone = fields.Char(
        string='Téléphone',
        tracking=True,
    )
    customer_company = fields.Char(
        string='Société / Entreprise',
    )
    notes = fields.Text(
        string='Remarques & Instructions',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'En attente'),
            ('sent', 'Envoyé par email'),
            ('confirmed', 'Confirmé'),
            ('converted', 'Converti en vente'),
            ('cancelled', 'Annulé'),
        ],
        string='État',
        default='draft',
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        'abdoo_web.pre_order.lines',
        'pre_order_id',
        string='Lignes de pré-commande',
        copy=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
    )
    lines_count = fields.Integer(
        string="Nombre d'articles",
        compute='_compute_totals',
        store=True,
    )
    amount_total = fields.Float(
        string='Montant Total',
        compute='_compute_totals',
        store=True,
        digits=(16, 2),
    )
    has_prices = fields.Boolean(
        string='Comporte des prix',
        compute='_compute_totals',
        store=True,
    )
    sale_order_id = fields.Many2one(
        'sm_sales.order',
        string='Commande Vente associée',
        readonly=True,
        copy=False,
    )

    @api.depends('line_ids.quantity', 'line_ids.price_subtotal', 'line_ids.price_unit')
    def _compute_totals(self):
        for record in self:
            total = 0.0
            count = 0
            has_price = False
            for line in record.line_ids:
                count += int(line.quantity)
                total += line.price_subtotal
                if line.price_unit > 0.0:
                    has_price = True
            record.amount_total = total
            record.lines_count = count
            record.has_prices = has_price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('abdoo_web.pre_order') or _('Nouveau')
        return super().create(vals_list)

    def action_send_email(self):
        self.ensure_one()
        template = self.env.ref('abdoo_web.mail_template_pre_order_confirmation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        if self.state == 'draft':
            self.state = 'sent'
        return True

    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
        return True

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
        return True

    def action_create_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            raise UserError(_("Une commande de vente existe déjà pour cette pré-commande (%s).") % self.sale_order_id.name)

        # Chercher ou créer un sm_sales.partner si nécessaire
        sales_partner = self.partner_id
        if not sales_partner and self.customer_name:
            sales_partner = self.env['sm_sales.partner'].search([
                '|',
                ('name', '=ilike', self.customer_name),
                ('email', '=ilike', self.customer_email or '____no_match____'),
            ], limit=1)
            if not sales_partner:
                sales_partner = self.env['sm_sales.partner'].create({
                    'name': self.customer_name,
                    'email': self.customer_email or False,
                    'phone': self.customer_phone or False,
                    'is_customer': True,
                    'company_id': self.company_id.id,
                })
            self.partner_id = sales_partner.id

        if not sales_partner:
            raise UserError(_("Veuillez sélectionner ou renseigner un client."))

        order_lines_vals = []
        for line in self.line_ids:
            order_lines_vals.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.description or line.product_id.name,
                'qty': line.quantity,
                'unit_price': line.price_unit or (line.product_id.default_price if not line.product_id.use_price_list else 0.0),
            }))

        sale_order = self.env['sm_sales.order'].create({
            'partner_id': sales_partner.id,
            'operation_type': 'order',
            'state': 'draft',
            'company_id': self.company_id.id,
            'note': self.notes or False,
            'order_lines': order_lines_vals,
        })

        self.write({
            'sale_order_id': sale_order.id,
            'state': 'converted',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Commande de vente'),
            'res_model': 'sm_sales.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }


class AbdooWebPreOrderLines(models.Model):
    _name = 'abdoo_web.pre_order.lines'
    _description = 'Lignes de pré-commande web'
    _order = 'pre_order_id, id'

    pre_order_id = fields.Many2one(
        'abdoo_web.pre_order',
        string='Pré-commande',
        ondelete='cascade',
        required=True,
        index=True,
    )
    product_id = fields.Many2one(
        'sm_sales.product',
        string='Article',
        required=True,
        ondelete='restrict',
    )
    product_code = fields.Char(
        string='Référence',
        related='product_id.code',
        readonly=True,
    )
    description = fields.Text(
        string='Désignation / Détails',
    )
    quantity = fields.Float(
        string='Quantité',
        default=1.0,
        required=True,
    )
    price_unit = fields.Float(
        string='Prix unitaire',
        digits=(16, 2),
    )
    price_subtotal = fields.Float(
        string='Sous-total',
        compute='_compute_subtotal',
        store=True,
        digits=(16, 2),
    )

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * (line.price_unit or 0.0)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name
            if not self.product_id.use_price_list:
                self.price_unit = self.product_id.default_price
            else:
                self.price_unit = 0.0
