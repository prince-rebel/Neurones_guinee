# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class DossierManagementExport(models.TransientModel):
    _name = "dossier.management.export"
    _description = "Dossier management export"

    type = fields.Selection([('all', 'Tous'), ('period', 'Sur une periode')], "Type", default="all")
    date_start = fields.Date("Date de début")
    date_to = fields.Date("Date de fin")

    def export_data(self):
        ds_object = self.env['neurones.dossier.manager']
        res = []
        _search = []
        if self.type == 'period':
            _search = [('date', '>=', self.date_start), ('date', '<=', self.date_to)]
            dossiers = ds_object.search(_search)
            if dossiers:
                return



