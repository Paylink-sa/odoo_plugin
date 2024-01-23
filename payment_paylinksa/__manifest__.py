# -*- coding: utf-8 -*-
{
    'name': "Payment Provider: paylink.sa",
    'summary': "Paylink provides you with a competitive payment gateway and solutions that are suitable for you!",
    'author': "paylink",
    'website': "https://paylink.sa",
    'category': 'Accounting/Payment Providers',
    'version': '1.0',
    'depends': ['payment'],
    'data': [
        'views/payment_paylink_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_method_data.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',

    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}
