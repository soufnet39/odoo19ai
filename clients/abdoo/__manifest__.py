# -*- coding: utf-8 -*-
{
    'name': 'Abdoo - Gestion Commerciale',
    'version': '19.0.1.2.0',
    'category': 'Smail',
    'summary': 'Adds extra fields to the product module (filter reference, brand, engine, fuel, etc.)',
    'description': """
        Abdoo Module
        ============
        This module extends the product template with additional fields
        related to filters, engine types, fuel types, and brands.

        Features:
        ---------
        * Reference Marque Filtre (Char)
        * Marque Maison (Many2one → abdoo.maison.marques)
        * Age moteur (Selection: Ancien / Nouveau)
        * Nature carburant (Selection: Essence / Diesel)
        * Moteur (Many2one → motors)
        * Type Moteur (Many2one → motor.types)
        * Marque de Filtre (Many2one → filter.marques)
        * Type de filtre (Selection: clim / gazoil / air / essence / huile)
    """,
    'author': 'SN',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'sm_base',
        'shakliyat',
        'sm_sales',
        'sm_purchases',
        'sm_stocks',
        'sm_boxes',   
        'sm_pos' 

       
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/zones_views.xml',
        'views/maison_marques_views.xml',
        'views/motors_views.xml',
        'views/motor_types_views.xml',
        'views/filter_marques_views.xml',
        'views/product_views.xml',
        # 'views/order_line_rank_views.xml',
        # 'views/purchase_views.xml',
        'views/abdoo_menus.xml',
        # 'views/listing.xml',
        # 'report/order_line_rank_report.xml',
        # 'report/sale_order_abdoo_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
