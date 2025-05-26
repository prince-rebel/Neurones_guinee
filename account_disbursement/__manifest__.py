# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account disbursement',
    'version': '1.1',
    'summary': 'Account',
    'sequence': 15,
    'license': 'LGPL-3',
    'description': """
    """,
    'depends': ['base', 'account', 'hr'],
    'data': [
        "security/group_user.xml",
        "security/ir.model.access.csv",
        "data/email_template_view.xml",
        "data/ir_sequence_data.xml",
        # "wizards/account_refused_wizard_view.xml",
        "views/account_disbursement_view.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
