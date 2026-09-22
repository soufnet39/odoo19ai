# -*- coding: utf-8 -*-
{
    'name': 'Transbelt',
    'summary': 'Transbelt Company Module',
    'description': """
        Module des additifs concernant transbelt company
    """,
    'author': 'Moussaoui smail',
    'website': '',
    'category': 'Smail',
    'version': '19.0.1.0.0',
    'depends': [
        'base',
        'mail',
        'sm_base',
        'sm_sales',
        'sm_boxes',
        'sm_stocks',
        'shakliyat',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',        
        'views/albelt_industry_views.xml',
        'views/albelt_raison_socio_views.xml',
        'views/menus.xml',
        'views/customer_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
