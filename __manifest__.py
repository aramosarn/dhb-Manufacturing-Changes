# -*- coding: utf-8 -*-
{
    'name': "dhb_mrp",

    'summary': """
      Modificacion de modelos y vistas para dhb modulo de  produccion""",

    'description': """
        Módificación para fabricación DHB
    """,

    'author': "Flex Consulting Group SPA",
    'website': "http://www.flexconsultinggroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'mrp',
                'purchase',
                'sale_management',
                'contacts',
                'todo',
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/views2.xml',
    ],

}