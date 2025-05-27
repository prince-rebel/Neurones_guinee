# -*- coding:utf-8 -*-


from odoo import api, fields, _, models


class AccountDisbursement(models.Model):
    _inherit = "account.disbursement"

    type_depense = fields.Selection([('project', 'Lié à un projet'), ('other', 'Autre')], default=False,
                                    string="Type de dépense", required=True)
    dossier_id = fields.Many2one("neurones.dossier.manager", "Dossier Commercial", required=False)