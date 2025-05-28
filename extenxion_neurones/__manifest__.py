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
    'author': 'Jean-Jonathan ARRA',
    'license': 'LGPL-3',
    'support': 'jonathan.arra@gmail.com',
    'depends': ['base', 'account', 'sale', 'purchase', 'contacts'],
    'data': [
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
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}