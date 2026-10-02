# -*- coding: utf-8 -*-
from odoo.tests import common


class TestAbdooWebPreOrder(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env['sm_sales.product.category'].create({
            'name': 'Filtres Test',
        })
        cls.product = cls.env['sm_sales.product'].create({
            'name': 'Filtre Huile Test',
            'code': 'FH-001',
            'default_price': 1200.0,
            'categ_id': cls.category.id,
            'is_published': True,
            'sale_ok': True,
        })

    def test_pre_order_creation_and_totals(self):
        """Tester la création d'une pré-commande et le calcul des montants et totaux."""
        pre_order = self.env['abdoo_web.pre_order'].create({
            'customer_name': 'Client Test',
            'customer_email': 'test@example.com',
            'customer_phone': '0661000000',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 3.0,
                    'price_unit': 1200.0,
                }),
            ],
        })

        self.assertTrue(pre_order.name.startswith('PRE/'))
        self.assertEqual(pre_order.lines_count, 3)
        self.assertEqual(pre_order.amount_total, 3600.0)
        self.assertTrue(pre_order.has_prices)
        self.assertEqual(pre_order.state, 'draft')

    def test_pre_order_confirmation_and_conversion(self):
        """Tester la confirmation et conversion d'une pré-commande en commande commerciale."""
        pre_order = self.env['abdoo_web.pre_order'].create({
            'customer_name': 'Garage Express',
            'customer_email': 'express@garage.dz',
            'customer_phone': '0555999888',
            'line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'quantity': 2.0,
                    'price_unit': 1200.0,
                }),
            ],
        })

        pre_order.action_confirm()
        self.assertEqual(pre_order.state, 'confirmed')

        # Conversion
        action = pre_order.action_create_sale_order()
        self.assertTrue(action)
        self.assertEqual(pre_order.state, 'converted')
        self.assertTrue(pre_order.sale_order_id)
        self.assertEqual(len(pre_order.sale_order_id.order_lines), 1)
        self.assertEqual(pre_order.partner_id._name, 'sm_sales.partner')
        self.assertEqual(pre_order.sale_order_id.partner_id.id, pre_order.partner_id.id)

    def test_pre_order_user_isolation(self):
        """Tester que chaque utilisateur ne voit que ses propres pré-commandes."""
        user_a = self.env['res.users'].create({
            'name': 'Client A',
            'login': 'client_a@test.dz',
            'email': 'client_a@test.dz',
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])],
        })
        user_b = self.env['res.users'].create({
            'name': 'Client B',
            'login': 'client_b@test.dz',
            'email': 'client_b@test.dz',
            'group_ids': [(6, 0, [self.env.ref('base.group_portal').id])],
        })

        order_a = self.env['abdoo_web.pre_order'].create({
            'customer_name': 'Client A',
            'customer_email': 'client_a@test.dz',
            'user_id': user_a.id,
            'line_ids': [(0, 0, {'product_id': self.product.id, 'quantity': 1.0, 'price_unit': 1200.0})],
        })
        order_b = self.env['abdoo_web.pre_order'].create({
            'customer_name': 'Client B',
            'customer_email': 'client_b@test.dz',
            'user_id': user_b.id,
            'line_ids': [(0, 0, {'product_id': self.product.id, 'quantity': 2.0, 'price_unit': 1200.0})],
        })

        # Consultation en tant qu'utilisateur A
        orders_visible_a = self.env['abdoo_web.pre_order'].with_user(user_a).search([])
        self.assertIn(order_a, orders_visible_a)
        self.assertNotIn(order_b, orders_visible_a)

        # Consultation en tant qu'utilisateur B
        orders_visible_b = self.env['abdoo_web.pre_order'].with_user(user_b).search([])
        self.assertIn(order_b, orders_visible_b)
        self.assertNotIn(order_a, orders_visible_b)


