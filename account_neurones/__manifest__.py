# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Update Neurones',
    'version': '0.1',
    'summary': 'Calcule de marge sur prix unitaires',
    'sequence': 1,
    'description':
        """ 
        """,
    'category': 'Sales',
    'author': 'Veone',
    'website': 'http://www.veone.net',
    'license': 'LGPL-3',
    'support': 'infos@veone.net',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/SequenceMonthlyManagerView.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}