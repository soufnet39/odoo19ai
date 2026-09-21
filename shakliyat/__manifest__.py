# -*- coding: utf-8 -*-
{
    'name': 'Shakliyat',
    'version': '19.0.1.11.0',
    'category': 'Smail',
    'summary': 'Custom theming and style overrides for the Odoo UI',
    'description': """
Shakliyat
=========
Layer of custom styling on top of the stock Odoo 19 design:
backend app chrome, buttons, forms and the frontend website/login pages.
""",
    'author': 'Moussaoui Smail',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'web',
        'base_setup',
    ],
    'data': [
        'views/landing_page.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        # Whole app UI (dashboard, forms, lists, settings, ...)
        'web.assets_backend': [
            'shakliyat/static/src/css/shakliyat_backend.css',
            'shakliyat/static/src/css/shakliyat_dark.css',
            'shakliyat/static/src/xml/cog_menu.xml',
            'shakliyat/static/src/xml/form_status_indicator.xml',
            'shakliyat/static/src/xml/leave_confirm_dialog.xml',
            'shakliyat/static/src/xml/landing_page.xml',
            'shakliyat/static/src/js/cog_menu.js',
            'shakliyat/static/src/js/form_status_indicator.js',
            'shakliyat/static/src/js/leave_confirm_dialog.js',
            'shakliyat/static/src/js/form_leave_confirm.js',
            'shakliyat/static/src/js/landing_page.js',
            'shakliyat/static/src/js/hide_discuss.js',
            'shakliyat/static/src/js/dark_mode.js',
        ],
        # Website + login page
        'web.assets_frontend': [
            'shakliyat/static/src/css/shakliyat_frontend.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
