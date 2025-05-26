# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class UpdateDossierCommercial(models.TransientModel):
    _name = "update.dossier_commercial"
    _description = "Update des dossiers commerciaux"

    def update_dossier_commerciaux(self):
        dossiers = self.env[self._context['active_model']].browse(self._context['active_ids'])
        if dossiers:
            for dc in dossiers:
                dc.reload_initial_data()
            dossiers.compute_committee_sale()
