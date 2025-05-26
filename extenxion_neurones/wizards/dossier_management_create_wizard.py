# -*- coding:utf-8 -*-


from odoo import api, models, fields, _


class DossierManagementCreateWizard(models.TransientModel):
    _name = "dossier.create_wizard"
    _description = "Wizard dossier create"

    #budget_template_id = fields.Many2one("account.budget_template", "Modèle de budget à utiliser", required=True)
