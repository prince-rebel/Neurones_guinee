{
    'name': 'Masques Impression Neurones',
    'description': """ 
    Gestion de:
        - Masques d'impression(Vente-Achat-Facturation)
        - Congés
            """,
    'author': 'Team Odoo(Veone)',
    'sequence': 1,
    'depends': ['base', 'web', 'hr', 'hr_holidays', 'sale', 'account', 'purchase', 'crm', 'stock', 'purchase', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'report/masques_neurones_reports.xml',
        'report/layout_templates.xml',
        'report/report_invoice.xml',
        'report/purchase_order_templates.xml',
        'report/purchase_quotation_templates.xml',
        'report/sale_report_templates.xml',
        'report/report_deliveryslip.xml',
        'views/custom_views.xml',
        'views/invoice_views.xml',
        #'data/layout_templates.xml',
        #'views/report_invoice.xml',
        'data/job.xml',
    ],
    'installable': True,
    'auto_install': False,
}
