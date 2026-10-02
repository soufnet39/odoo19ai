# -*- coding: utf-8 -*-
{
    'name': 'Abdoo Web',
    'version': '19.0.1.0.0',
    'category': 'Smail',
    'summary': 'Catalogue e-commerce, panier et pré-commandes pour Abdoo',
    'description': """
        Abdoo Web Module
        ================
        * Page catalogue e-commerce groupée par catégorie
        * Contrôle de visibilité des prix réservé aux utilisateurs autorisés
        * Panier interactif avec stockage persistant
        * Enregistrement en pré-commande (abdoo_web.pre_order & abdoo_web.pre_order.lines)
        * Envoi automatique par email
        * Conversion en commande de vente en un clic
    """,
    'author': 'Moussaoui Smail',
    'license': 'LGPL-3',
    'depends': [
        'abdoo',
        'web',
        'portal',
        'website',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/website_menu_data.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/pre_order_views.xml',
        'views/catalog_templates.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'abdoo_web/static/src/css/abdoo_web.css',
            'abdoo_web/static/src/js/abdoo_web.js',
        ],
        'web.assets_frontend': [
            'abdoo_web/static/src/css/abdoo_web.css',
            'abdoo_web/static/src/js/abdoo_web.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
