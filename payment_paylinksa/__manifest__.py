# -*- coding: utf-8 -*-
{
    'name': "Payment Solution by Paylink1",
    'summary': "Experience seamless payment solutions with Paylink, the premium payment gateway company in Saudi Arabia",
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

    'license': 'LGPL-3',
    'images': ['static/description/banner.png'],
}
