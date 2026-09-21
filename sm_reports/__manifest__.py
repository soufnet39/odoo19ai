# -*- coding: utf-8 -*-
{
    'name': 'SM Reports',
    'version': '19.0.1.0.0',
    'category': 'Smail',
    'summary': 'Reports module',
    'description': """
SM Reports
==========
Reports for the Smail ecosystem.
    """,
    'author': 'SM',
    'website': '',
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
        'data/refresh_data.xml',
        'reports/supplier_purchase_reports.xml',
        'reports/customer_sales_reports.xml',
        'views/customer_sales_views.xml',
        'views/supplier_purchase_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sm_reports/static/src/css/customer_sales.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}