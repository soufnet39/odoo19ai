# -*- coding: utf-8 -*-
{
    'name': 'SM Factures',
    'summary': 'Module de facturation client',
    'description': """
        Module de facturation client
        ====================
        Un module personnalisé pour la gestion des factures clients.
        Mirrors sm_sales.order (sans les proformas) en réutilisant sm_sales.partner
        et sm_sales.product comme modèles de partenaires et de produits.
    """,
    'author': 'SM',
    'website': '',
    'category': 'Smail',
    'version': '19.0.1.0.0',
    'depends': [
        'base',
        'mail',
        'sm_base',
        'sm_sales',
        'sm_boxes',
        'shakliyat',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/invoices_views.xml',
        'views/orders_views.xml',
        'views/invoices_menu.xml',
        'views/res_config_settings_views.xml',
        'reports/invoice_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sm_invoices/static/src/js/landing_page.js',
        ],
    },
    'installable': True,
    'application': True,
    'icon': 'sm_invoices/static/description/icon.png',
    'auto_install': False,
    'license': 'LGPL-3',
}
