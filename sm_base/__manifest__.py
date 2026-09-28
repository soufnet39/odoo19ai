# -*- coding: utf-8 -*-
{
    "name": "SM Base",
    "version": "19.0.1.0.0",
    "category": "Smail",
    "summary": "Module de base : divisions administratives algériennes et données partagées",
    "description": """
Base SM
=======
Module fondamental fournissant les données administratives algériennes (wilayas)
et les modèles partagés de l'écosystème Smail.
    """,
    "author": "Moussaoui Smail",
    "license": "LGPL-3",
    "depends": [
        "base",
        "shakliyat",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "views/wilayates_views.xml",
        "views/res_company_views.xml",
        "views/menu.xml",
        "data/wilayates_data.xml",
        "data/apps_menu.xml",
        'views/ir_sequence_views.xml',
        'reports/report_external_layout.xml',
        'views/about_mizan_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "sm_base/static/src/css/about_mizan.css",
            "sm_base/static/src/xml/about_mizan.xml",
            "sm_base/static/src/js/landing_page.js",
            "sm_base/static/src/js/about_mizan.js",
            "sm_base/static/src/js/user_menu.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
