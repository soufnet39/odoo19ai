{
    'name': 'SM Ventes',
    'summary': 'Module de ventes personnalisé',
    'description': """
        Module de ventes personnalisé
        ====================
        Un module personnalisé pour la gestion des ventes.
    """,
    'author': 'SM',
    'website': '',
    'category': 'Smail',
    'version': '19.0.1.0.0',
    'depends': [
        'base',
        'base_setup',
        'mail',        
        'sm_base',
        'shakliyat',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',


        'data/decimal_precision.xml',
        'data/payment_data.xml',
        'data/pricelist_data.xml',
        'data/sequences.xml',
        'data/banks_data.xml',

        'views/payment_mode_views.xml',
        'views/payment_method_views.xml',
        'views/sale_condition_views.xml',
        'views/offer_validity_views.xml',
        'views/product_category_views.xml',
        'views/product_views.xml',
        'views/customer_views.xml',
        'views/pricelist_views.xml',
        'views/banks_views.xml',
        'views/order_views.xml',
        'views/quotation_views.xml',
        'reports/order_report.xml',
        'reports/quotation_report.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'icon': 'sm_sales/static/description/icon.png',
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'sm_sales/static/src/js/landing_page.js',
            'sm_sales/static/src/js/sheet_state.js',
            'sm_sales/static/src/css/sheet_state.css',
        ],
    },
}
