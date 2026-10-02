# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request


class AbdooWebController(http.Controller):

    def _can_see_prices(self):
        """Détermine si l'utilisateur courant est autorisé à voir les prix du catalogue."""
        user = request.env.user
        if not user or user._is_public():
            return False

        # Utilisateur interne ou groupe spécifique
        if user.has_group('base.group_user') or user.has_group('abdoo_web.group_catalog_prices'):
            return True

        # Autorisation sur le client commercial sm_sales.partner
        if user.email:
            sales_partner = request.env['sm_sales.partner'].sudo().search([
                ('email', '=', user.email),
                ('can_view_catalog_prices', '=', True),
            ], limit=1)
            if sales_partner:
                return True

        return False

    @http.route([
        '/boutique',
        '/boutique/category/<int:category_id>',
        '/catalog',
        '/catalog/category/<int:category_id>',
        '/catalogue',
    ], type='http', auth='public', website=True, sitemap=True)
    def catalog(self, category_id=None, search=None, **kwargs):
        """Page principale du catalogue e-commerce Abdoo."""
        Product = request.env['sm_sales.product'].sudo()
        Category = request.env['sm_sales.product.category'].sudo()

        domain = [('is_published', '=', True), ('sale_ok', '=', True), ('active', '=', True)]
        if search:
            domain += ['|', '|', ('name', 'ilike', search), ('code', 'ilike', search), ('description', 'ilike', search)]
        if category_id:
            domain += [('categ_id', '=', category_id)]

        products = Product.search(domain, order='categ_id, name')

        # Toutes les catégories ayant au moins un produit publié
        all_published = Product.search([('is_published', '=', True), ('sale_ok', '=', True), ('active', '=', True)])
        published_categ_ids = all_published.mapped('categ_id.id')
        categories = Category.browse(published_categ_ids).sorted(key=lambda c: c.name or '')

        # Regroupement des produits par catégorie
        grouped_products = {}
        for product in products:
            categ_name = product.categ_id.name if product.categ_id else _('Sans catégorie')
            categ_id_val = product.categ_id.id if product.categ_id else 0
            key = (categ_id_val, categ_name)
            if key not in grouped_products:
                grouped_products[key] = []
            grouped_products[key].append(product)

        can_see_prices = self._can_see_prices()

        # Coordonnées pré-remplies si utilisateur connecté via sm_sales.partner
        user = request.env.user
        sales_partner = False
        if not user._is_public() and user.email:
            sales_partner = request.env['sm_sales.partner'].sudo().search([('email', '=', user.email)], limit=1)

        customer_info = {
            'name': (sales_partner.name if sales_partner else (user.name or '')) if not user._is_public() else '',
            'email': (sales_partner.email if sales_partner else (user.email or '')) if not user._is_public() else '',
            'phone': (sales_partner.phone or sales_partner.mobile or '') if sales_partner else (user.phone or ''),
            'company': (user.company_id.name or '') if not user._is_public() else '',
        }

        import json
        values = {
            'categories': categories,
            'selected_category_id': category_id,
            'search_term': search or '',
            'grouped_products': grouped_products,
            'products_count': len(products),
            'can_see_prices': can_see_prices,
            'is_logged_in': not user._is_public(),
            'customer_info': customer_info,
            'catalog_config_json': json.dumps({
                'can_see_prices': can_see_prices,
                'is_logged_in': not user._is_public(),
                'customer_info': customer_info,
            }),
        }

        return request.render('abdoo_web.catalog_page', values)

    @http.route('/catalog/pre_order/submit', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def submit_pre_order(self, **post):
        """Enregistrement d'une pré-commande depuis le panier web."""
        customer_name = post.get('customer_name', '').strip()
        customer_email = post.get('customer_email', '').strip()
        customer_phone = post.get('customer_phone', '').strip()
        customer_company = post.get('customer_company', '').strip()
        notes = post.get('notes', '').strip()
        action_type = post.get('action_type', 'save')  # 'save' ou 'email'
        lines_data = post.get('lines', [])

        if not customer_name:
            return {'success': False, 'error': _('Veuillez renseigner votre nom ou prénom.')}

        if action_type == 'email' and not customer_email:
            return {'success': False, 'error': _('Veuillez renseigner votre adresse e-mail pour recevoir la confirmation.')}

        if not lines_data:
            return {'success': False, 'error': _('Votre panier est vide.')}

        can_see_prices = self._can_see_prices()
        user = request.env.user
        # Recherche ou création d'un client commercial sm_sales.partner
        sales_partner = False
        if customer_email or customer_name:
            sales_partner = request.env['sm_sales.partner'].sudo().search([
                '|',
                ('email', '=', customer_email),
                ('name', '=ilike', customer_name),
            ], limit=1)
            if not sales_partner and customer_name:
                sales_partner = request.env['sm_sales.partner'].sudo().create({
                    'name': customer_name,
                    'email': customer_email or False,
                    'phone': customer_phone or False,
                    'is_customer': True,
                    'company_id': request.env.company.id,
                })

        # Construction des lignes
        order_lines = []
        Product = request.env['sm_sales.product'].sudo()

        for item in lines_data:
            prod_id = item.get('product_id')
            qty = float(item.get('quantity', 1.0))
            if qty <= 0:
                continue
            product = Product.browse(prod_id)
            if not product.exists():
                continue

            # Prix unitaire sécurisé côté serveur : visible uniquement si autorisé
            unit_price = 0.0
            if can_see_prices:
                unit_price = float(product.default_price) if not product.use_price_list else 0.0

            order_lines.append((0, 0, {
                'product_id': product.id,
                'description': product.name + (f" [{product.code}]" if product.code else ""),
                'quantity': qty,
                'price_unit': unit_price,
            }))

        if not order_lines:
            return {'success': False, 'error': _('Aucun article valide dans le panier.')}

        # Création de la pré-commande
        pre_order_vals = {
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'customer_company': customer_company,
            'notes': notes,
            'partner_id': sales_partner.id if sales_partner else False,
            'user_id': user.id if not user._is_public() else False,
            'line_ids': order_lines,
            'state': 'draft',
        }

        pre_order = request.env['abdoo_web.pre_order'].sudo().create(pre_order_vals)

        # Envoi d'email si demandé
        if action_type == 'email':
            try:
                pre_order.action_send_email()
            except Exception as e:
                # En cas d'erreur de serveur SMTP, la pré-commande est tout de même sauvegardée
                return {
                    'success': True,
                    'order_id': pre_order.id,
                    'order_name': pre_order.name,
                    'warning': _('Pré-commande enregistrée, mais un problème est survenu lors de l\'envoi de l\'email : %s') % str(e),
                }

        return {
            'success': True,
            'order_id': pre_order.id,
            'order_name': pre_order.name,
            'action_type': action_type,
            'message': _('Votre pré-commande %s a été enregistrée avec succès.') % pre_order.name,
        }


try:
    from odoo.addons.portal.controllers.portal import CustomerPortal
except ImportError:
    CustomerPortal = object


class AbdooCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'pre_order_count' in counters:
            user = request.env.user
            if not user._is_public():
                domain = ['|', ('user_id', '=', user.id), ('create_uid', '=', user.id)]
                if user.email:
                    domain = ['|', '|', ('user_id', '=', user.id), ('create_uid', '=', user.id), ('customer_email', '=', user.email)]
                values['pre_order_count'] = request.env['abdoo_web.pre_order'].sudo().search_count(domain)
            else:
                values['pre_order_count'] = 0
        return values

    @http.route(['/mes-precommandes', '/my/pre_orders', '/my/pre-orders'], type='http', auth='user', website=True)
    def portal_my_pre_orders(self, **kwargs):
        """Affiche l'historique des pré-commandes de l'utilisateur connecté uniquement."""
        user = request.env.user
        domain = ['|', ('user_id', '=', user.id), ('create_uid', '=', user.id)]
        if user.email:
            domain = ['|', '|', ('user_id', '=', user.id), ('create_uid', '=', user.id), ('customer_email', '=', user.email)]

        pre_orders = request.env['abdoo_web.pre_order'].sudo().search(domain, order='date desc, id desc')
        can_see_prices = AbdooWebController()._can_see_prices()

        values = {
            'pre_orders': pre_orders,
            'can_see_prices': can_see_prices,
            'page_name': 'pre_orders',
        }
        return request.render('abdoo_web.portal_my_pre_orders', values)

    @http.route(['/mes-precommandes/<int:order_id>', '/my/pre_orders/<int:order_id>', '/my/pre-orders/<int:order_id>'], type='http', auth='user', website=True)
    def portal_my_pre_order_detail(self, order_id=None, **kwargs):
        """Affiche les détails d'une pré-commande spécifique de l'utilisateur."""
        user = request.env.user
        pre_order = request.env['abdoo_web.pre_order'].sudo().browse(order_id)
        if not pre_order.exists():
            return request.redirect('/mes-precommandes')

        # Contrôle d'accès strict : l'utilisateur ne peut voir que sa propre commande (sauf manager/admin)
        is_owner = (
            pre_order.user_id.id == user.id or
            pre_order.create_uid.id == user.id or
            (user.email and pre_order.customer_email == user.email)
        )
        is_manager = user.has_group('abdoo.abdoo_manager') or user.has_group('base.group_system')
        if not (is_owner or is_manager):
            return request.redirect('/mes-precommandes')

        can_see_prices = AbdooWebController()._can_see_prices()

        values = {
            'pre_order': pre_order,
            'can_see_prices': can_see_prices,
            'page_name': 'pre_order_detail',
        }
        return request.render('abdoo_web.portal_my_pre_order_detail', values)
