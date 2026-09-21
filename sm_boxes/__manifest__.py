# -*- coding: utf-8 -*-
{
    "name": "SM Finances",
    "version": "19.0.1.0.0",
    "category": "Smail",
    "summary": "Module de gestion des caisses",
    "description": """
SM Caisses
========
Module de gestion des caisses dans l'écosystème Smail.
    """,
    "author": "Moussaoui Smail",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "sm_base",
        "sm_sales",
        "sm_purchases",
        "shakliyat",
    ],
    "data": [
        'security/security.xml',
        "security/ir.model.access.csv",
        'security/rules.xml',

        "data/config_data.xml",
        "views/comptes_views.xml",
        "views/menu.xml",
        "views/operations_views.xml",
        "views/order_views.xml",
        "views/purchase_views.xml",
        "views/res_config_settings_views.xml",
        
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "sm_boxes/static/src/js/landing_page.js",
        ],
    },
}
