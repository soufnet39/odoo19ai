# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models, _


class SmPosSession(models.Model):
    _name = 'sm_pos.session'
    _description = 'Session du point de vente'
    _order = 'id desc'

    POS_SESSION_STATE = [
        ('opening_control', "Contrôle à l'ouverture"),
        ('opened', 'En cours'),
        ('closing_control', 'Contrôle à la fermeture'),
        ('closed', 'Fermée'),
    ]

    name = fields.Char(string='Identifiant de session', readonly=True, default='/')
    config_id = fields.Many2one('sm_pos.config', string='Point de vente', required=True, index=True)
    company_id = fields.Many2one('res.company', related='config_id.company_id',
                                 string='Société', readonly=True)
    user_id = fields.Many2one('res.users', string='Ouverte par', required=True, index=True,
                              default=lambda self: self.env.user, ondelete='restrict')

    state = fields.Selection(POS_SESSION_STATE, string='État', required=True, readonly=True,
                             index=True, copy=False, default='opening_control')
    start_at = fields.Datetime(string="Date d'ouverture", readonly=True)
    stop_at = fields.Datetime(string='Date de fermeture', readonly=True, copy=False)
    opening_notes = fields.Text(string="Notes d'ouverture")
    closing_notes = fields.Text(string='Notes de fermeture')

    cash_register_balance_start = fields.Float(string='Solde initial', digits='Product Price')
    cash_register_balance_end_real = fields.Float(string='Solde final', readonly=True,
                                                  digits='Product Price')
    cash_register_balance_end = fields.Float(string='Solde théorique de clôture',
                                             compute='_compute_cash_balance', digits='Product Price')
    cash_register_difference = fields.Float(string='Différence', compute='_compute_cash_balance',
                                            digits='Product Price')

    order_ids = fields.One2many('sm_sales.order', 'session_id', string='Commandes')
    order_count = fields.Integer(compute='_compute_order_count')
    payment_ids = fields.One2many('sm_boxes.operations', 'session_id', string='Paiements')

    @api.depends('order_ids')
    def _compute_order_count(self):
        for session in self:
            session.order_count = len(session.order_ids)

    @api.depends('cash_register_balance_start', 'payment_ids.amount', 'payment_ids.sens', 'payment_ids.mode')
    def _compute_cash_balance(self):
        for session in self:
            total = session.cash_register_balance_start
            for payment in session.payment_ids:
                if payment.mode == 'sold':
                    total += payment.amount if payment.sens == 'credit' else -payment.amount
            session.cash_register_balance_end = total
            session.cash_register_difference = session.cash_register_balance_end_real - total

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sm_pos.session')
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    def action_pos_session_open(self):
        self.ensure_one()
        self.write({'state': 'opened', 'start_at': fields.Datetime.now()})
        return True

    def action_pos_session_closing_control(self):
        self.ensure_one()
        self.write({'state': 'closing_control'})
        return True

    def action_pos_session_close(self):
        self.ensure_one()
        self.write({'state': 'closed', 'stop_at': fields.Datetime.now()})
        return True

    @api.model
    def open_session(self, config_id, opening_cash=0.0):
        """Ouvre une nouvelle session pour la configuration donnée (utilisée par l'interface du point de vente)."""
        config = self.env['sm_pos.config'].browse(config_id)
        open_session = self.search([
            ('config_id', '=', config.id),
            ('state', 'in', ('opening_control', 'opened', 'closing_control')),
        ], limit=1)
        if open_session:
            return {'id': open_session.id, 'name': open_session.name, 'state': open_session.state}
        session = self.create({
            'config_id': config.id,
            'user_id': self.env.user.id,
            'cash_register_balance_start': opening_cash,
        })
        session.action_pos_session_open()
        return {'id': session.id, 'name': session.name, 'state': session.state}

    def close_session(self, closing_cash=0.0, notes=''):
        """Ferme la session (utilisée par l'interface du point de vente)."""
        self.ensure_one()
        self.write({
            'cash_register_balance_end_real': closing_cash,
            'closing_notes': notes,
        })
        self.action_pos_session_close()
        return {'id': self.id, 'name': self.name, 'state': self.state}

    def get_closing_data(self):
        """Retourne les montants nécessaires à l'écran de contrôle de fermeture."""
        self.ensure_one()
        return {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'cash_register_balance_start': self.cash_register_balance_start,
            'cash_register_balance_end': self.cash_register_balance_end,
            'cash_register_difference': self.cash_register_difference,
            'order_count': self.order_count,
            'payment_count': len(self.payment_ids),
        }

    def start_closing_control(self):
        """Place la session en contrôle de fermeture et retourne les montants de clôture."""
        self.ensure_one()
        self.action_pos_session_closing_control()
        return self.get_closing_data()

    def resume_session(self):
        """Rétablit une session en contrôle de fermeture à l'état ouverte (annule la fermeture)."""
        self.ensure_one()
        if self.state == 'closing_control':
            self.write({'state': 'opened'})
        return {'id': self.id, 'name': self.name, 'state': self.state}

    # ------------------------------------------------------------------
    # POS frontend data API
    # ------------------------------------------------------------------
    def load_pos_data(self):
        """Retourne toutes les données nécessaires à l'interface du point de vente pour cette session."""
        self.ensure_one()
        config = self.config_id
        pricelist = config.pricelist_id

        products = self.env['sm_sales.product'].search([('sale_ok', '=', True), ('active', '=', True)])
        product_data = []
        for product in products:
            price = product.default_price
            if pricelist:
                pl_price = self.env['sm_sales.pricelist.price'].search([
                    ('pricelist_id', '=', pricelist.id),
                    ('product_id', '=', product.id),
                ], limit=1)
                if pl_price:
                    price = pl_price.price
            product_data.append({
                'id': product.id,
                'name': product.name,
                'code': product.code or '',
                'categ_id': product.categ_id.id if product.categ_id else False,
                'categ_name': product.categ_id.name if product.categ_id else '',
                'price': price,
                'image_128': product.image_128 and base64.b64encode(product.image_128).decode() or False,
            })

        categories = [{'id': c.id, 'name': c.name}
                      for c in self.env['sm_sales.product.category'].search([])]
        partners = [{'id': p.id, 'name': p.name, 'phone': p.phone or p.mobile or ''}
                    for p in self.env['sm_sales.partner'].search(
                        [('is_customer', '=', True), ('active', '=', True)], limit=200)]
        payment_modes = [{'id': m.id, 'name': m.name, 'nature': m.nature}
                         for m in config.payment_mode_ids]

        # Commandes récentes de la session pour l'onglet Commandes
        recent_orders = []
        for o in self.env['sm_sales.order'].sudo().search([
            ('session_id', '=', self.id),
            ('is_pos_order', '=', True),
        ], order='id desc', limit=50):
            recent_orders.append({
                'id': o.id,
                'name': o.name,
                'date': o.date and o.date.strftime('%Y-%m-%d') or '',
                'partner_name': o.partner_id.name if o.partner_id else 'Client comptoir',
                'amount_ttc': o.amount_ttc,
                'amount_ht': o.amount_ht,
                'amount_tva': o.amount_tva,
                'state': o.state,
                'lines': [{'name': l.name, 'qty': l.qty, 'unit_price': l.unit_price, 'price_total': l.price_total} for l in o.order_lines],
            })

        return {
            'session': {
                'id': self.id,
                'name': self.name,
                'state': self.state,
                'cash_register_balance_start': self.cash_register_balance_start,
                'cash_register_balance_end': self.cash_register_balance_end,
            },
            'user': {
                'id': self.env.user.id,
                'name': self.env.user.name,
            },
            'company': {
                'id': self.company_id.id,
                'name': self.company_id.name,
                'currency': self.company_id.currency_id.symbol or 'DA',
            },
            'config': {
                'id': config.id,
                'name': config.name,
                'stock_id': config.stock_id.id,
                'pricelist_id': config.pricelist_id.id if config.pricelist_id else False,
                'boxe_id': config.boxe_id.id,
            },
            'products': product_data,
            'categories': categories,
            'partners': partners,
            'payment_modes': payment_modes,
            'recent_orders': recent_orders,
        }

    def sync_pos_order(self, order_vals):
        """Crée ou met à jour une commande du point de vente (sm_sales.order) depuis l'interface."""
        self.ensure_one()
        config = self.config_id

        order_id = order_vals.get('id')
        lines = order_vals.get('lines', [])
        partner_id = order_vals.get('partner_id') or False
        note = order_vals.get('note') or ''
        discount_rate = float(order_vals.get('discount_rate') or 0.0)

        line_vals = []
        for line in lines:
            product = self.env['sm_sales.product'].sudo().browse(line['product_id'])
            line_vals.append((0, 0, {
                'product_id': product.id,
                'name': line.get('name') or product.name,
                'qty': float(line.get('qty', 1.0)),
                'unit_price': float(line.get('unit_price', product.default_price)),
            }))

        order_vals_dict = {
            'operation_type': 'order',
            'session_id': self.id,
            'pos_config_id': config.id,
            'is_pos_order': True,
            'partner_id': partner_id,
            'stock_id': config.stock_id.id,
            'note': note,
            'order_lines': line_vals,
        }

        if discount_rate > 0:
            order_vals_dict['remise_exist'] = True
            order_vals_dict['remise_methode'] = 'taux'
            order_vals_dict['remise_taux'] = discount_rate

        order_model = self.env['sm_sales.order'].sudo()
        if order_id:
            order = order_model.browse(order_id)
            order_vals_dict['order_lines'] = [(5, 0, 0)] + line_vals
            order.write(order_vals_dict)
        else:
            order = order_model.create(order_vals_dict)

        # Confirme et marque comme livrée
        try:
            if order.state == 'draft':
                order.action_confirm()
            order.action_delivered()
        except Exception:
            pass

        return {
            'id': order.id,
            'name': order.name,
            'amount_ttc': order.amount_ttc,
            'amount_ht': order.amount_ht,
            'amount_tva': order.amount_tva,
            'date': order.date and order.date.strftime('%Y-%m-%d') or fields.Date.today().strftime('%Y-%m-%d'),
            'partner_name': order.partner_id.name if order.partner_id else 'Client comptoir',
            'lines': [{'name': l.name, 'qty': l.qty, 'unit_price': l.unit_price, 'price_total': l.price_total} for l in order.order_lines],
        }

    def add_payment(self, order_id, payment_mode_id, amount):
        """Enregistre un paiement du point de vente (sm_boxes.operations) pour une commande."""
        self.ensure_one()
        config = self.config_id
        order = self.env['sm_sales.order'].sudo().browse(order_id)
        payment_mode = self.env['sm_sales.payment.mode'].sudo().browse(payment_mode_id)
        mode_map = {'cash': 'sold', 'cheque': 'bank', 'transfer': 'virement', 'other': 'sold'}
        payment = self.env['sm_boxes.operations'].sudo().create({
            'operation': 'encaissement',
            'sens': 'credit',
            'boxe_id': config.boxe_id.id,
            'name': f"POS {self.name} - {order.name}",
            'amount': amount,
            'mode': mode_map.get(payment_mode.nature, 'sold'),
            'payment_mode_id': payment_mode.id,
            'order_id': order.id,
            'session_id': self.id,
            'partner_id': order.partner_id.id if order.partner_id else False,
            'date': fields.Date.today(),
        })
        return {'id': payment.id, 'name': payment.name, 'amount': payment.amount}

    def get_receipt_data(self, order_id):
        """Fournit toutes les informations nécessaires à l'impression directe du reçu de caisse."""
        self.ensure_one()
        order = self.env['sm_sales.order'].sudo().browse(order_id)
        return {
            'order_name': order.name,
            'date': order.date and order.date.strftime('%d/%m/%Y') or fields.Date.today().strftime('%d/%m/%Y'),
            'company_name': self.company_id.name,
            'pos_name': self.config_id.name,
            'cashier_name': self.user_id.name,
            'partner_name': order.partner_id.name if order.partner_id else 'Client comptoir',
            'amount_ht': order.amount_ht,
            'amount_tva': order.amount_tva,
            'amount_ttc': order.amount_ttc,
            'currency': self.company_id.currency_id.symbol or 'DA',
            'lines': [{
                'name': l.name,
                'qty': l.qty,
                'unit_price': l.unit_price,
                'price_total': l.price_total,
            } for l in order.order_lines],
        }