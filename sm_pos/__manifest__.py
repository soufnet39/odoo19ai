# -*- coding: utf-8 -*-
{
    "name": "Comptoire SM",
    "version": "19.0.1.0.0",
    "category": "Smail",
    "summary": "Point de vente",
    "description": """
Point de vente SM
======
Module de point de vente pour l'écosystème Smail.

Les commandes du point de vente sont des enregistrements `sm_sales.order` (operation_type='order') créés
via une interface de caisse dédiée. Les paiements sont enregistrés comme
`sm_boxes.operations` (encaissement) et les livraisons sont gérées à l'aide
des champs `sm_stocks` existants sur `sm_sales.order`.
    """,
    "author": "Moussaoui Smail",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "sm_base",
        "sm_sales",
        "sm_purchases",
        "sm_stocks",
        "sm_boxes",
        "shakliyat",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/config_views.xml",
        "views/session_views.xml",
        "views/order_views.xml",
        "views/menu.xml",
        "views/res_config_settings_views.xml",
        "reports/receipt.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "sm_pos/static/src/css/pos.css",
            "sm_pos/static/src/app/pos_app.xml",
            "sm_pos/static/src/screens/session_screen.xml",
            "sm_pos/static/src/screens/product_screen.xml",
            "sm_pos/static/src/screens/payment_screen.xml",
            "sm_pos/static/src/screens/closing_screen.xml",
            "sm_pos/static/src/components/product_card.xml",
            "sm_pos/static/src/components/order_line.xml",
            "sm_pos/static/src/components/numpad.xml",
            "sm_pos/static/src/services/pos_service.js",
            "sm_pos/static/src/components/product_card.js",
            "sm_pos/static/src/components/order_line.js",
            "sm_pos/static/src/components/numpad.js",
            "sm_pos/static/src/screens/session_screen.js",
            "sm_pos/static/src/screens/product_screen.js",
            "sm_pos/static/src/screens/payment_screen.js",
            "sm_pos/static/src/screens/closing_screen.js",
            "sm_pos/static/src/app/pos_app.js",
            "sm_pos/static/src/js/landing_page.js",
        ],
    },
}
