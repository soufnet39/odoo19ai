{
    'name': 'SM Achats',
    'summary': 'Module d\'achats personnalisé',
    'description': """
        Module d'achats personnalisé
        ====================
        Un module personnalisé pour la gestion des achats.
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
        'sm_sales',
        'shakliyat',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/suppliers_views.xml',
        'views/product.xml',
        'views/purchase_views.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml',
        'reports/purchase_report.xml',
    ],
    'installable': True,
    'application': True,
    'icon': 'sm_purchases/static/description/icon.png',
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'sm_purchases/static/src/js/landing_page.js',
        ],
    },
}
