# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class AccountDisbursementRefusedWizard(models.TransientModel):
    _name = "account.disbursement_refused_wizard"
    _description = "Disbursement refused management"

    name = fields.Text("Motif de refus", required=True)

    def action_refused(self):
        context = self.env.context
        instance = self.env[context.get("active_model")].search([('id', '=', context.get('active_id'))])
        if instance:
            for wiz in self:
                instance.motif_ruefus = wiz.name
                instance.action_refused()
