{
    'name': 'Masques Impression Neurones',
    'description': """ 
    Gestion de:
        - Masques d'impression(Vente-Achat-Facturation)
        - Congés
            """,
    'author': 'Djakaridja',
    'sequence': 3,
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'hr', 'hr_holidays', 'sale', 'account', 'purchase', 'crm', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'report/masques_neurones_reports.xml',
        'report/template_neurones.xml',
        'views/custom_views.xml',
        'views/invoice_views.xml',
        'views/report_deliveryslip.xml',
        'data/layout_templates.xml',
        # 'views/purchase_order_templates.xml',
        # 'views/purchase_quotation_templates.xml',
        #'views/report_invoice.xml',
        'views/sale_report_templates.xml',
        'data/job.xml',
    ],
    'installable': True,
    'auto_install': False,
}
