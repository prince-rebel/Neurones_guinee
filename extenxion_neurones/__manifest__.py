# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Neurones Extension',
    'version': '0.1',
    'summary': 'Neuronnes management',
    'sequence': 1,
    'description':
        """ 
        """,
    'category': 'Customization',
    'author': 'Veone',
    'license': 'LGPL-3',
    'support': 'info@veone.net',
    'depends': ['base', 'account', 'sale', 'purchase', 'contacts', 'account_disbursement', 'masques_neurones'],
    'data': [
        "security/security_view.xml",
        "security/ir.model.access.csv",
        "data/sequence_data_view.xml",
        "data/mail_template_data.xml",
        "reports/report_menu_view.xml",
        "views/res_company_view.xml",
        "views/report_dossier_commercial.xml",
        "views/saleOrderView.xml",
        "views/purchaseOrderView.xml",
        "views/accountInvoiceView.xml",
        "views/neurones_dossier_managment_view.xml",
        "views/accountDisbrusementView.xml",
        "wizards/update_dossier_commercial.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
