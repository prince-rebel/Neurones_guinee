# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Margin calculation',
    'version': '0.1',
    'summary': 'Calcule de marge sur prix unitaires',
    'sequence': 1,
    'description':
        """ 
            Sale Margin calculation
            Automatisation du calcul des prix unitaires des articles sur dévis.
        """,
    'category': 'Sales',
    'author': 'Veone SARL.',
    'website': 'http://www.veone.net',
    'license': 'LGPL-3',
    'support': 'infos@veone.net',
    'depends': ['base_setup', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/margin_calculation_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
