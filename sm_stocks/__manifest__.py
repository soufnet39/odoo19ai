# -*- coding: utf-8 -*-

{
    'name': 'SM Stocks',
    'version': '19.0.1.0.0',
    'summary': 'Stock Management Module',
    'description': """
        SM Stocks Module
    """,
    'category': 'Smail',
    'author': 'SM',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'sm_base', 'sm_sales', 'sm_purchases', 'shakliyat'],
    'data': [
        'security/security.xml',
        "security/ir.model.access.csv",
        'security/rules.xml',

        #  "data/sm_boxes_config_data.xml",
        'views/stocks_views.xml',
        'views/order_views.xml',
        'views/quotation_views.xml',
        'views/purchase_views.xml',
        'views/movement_views.xml',

        'views/only_receipt_views.xml',
        'views/only_delivery_views.xml',

        'reports/report_delivery.xml',
        'reports/report_receipt.xml',

        'views/menu.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'sm_stocks/static/src/js/landing_page.js',
        ],
    },
}