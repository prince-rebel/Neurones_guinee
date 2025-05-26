# -*- coding:utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import Warning, ValidationError


class committeeSetting(models.Model):
    _name = "committee.setting"
    _description = "committee setting management"

    name = fields.Char("Libellé", required=True)
    code = fields.Char("Code", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif(ve)", default=True)
    line_ids = fields.One2many("committee.setting.line", 'committee_setting_id', 'Société', required=False)
    company_id = fields.Many2one("res.company", 'Société', required=False)


class committeeSettingLine(models.Model):
    _name = "committee.setting.line"
    _description = "committee line setting management"

    name = fields.Char("Libellé", required=True)
    rate = fields.Float("% commissions", required=True)
    committee_rate_min = fields.Float("% de marge minimale", required=True)
    committee_rate_max = fields.Float("% de marge maximale", required=True)
    description = fields.Text("Description")
    active = fields.Boolean("Actif(ve)", default=True)
    committee_setting_id = fields.Many2one('committee.setting', 'Parent', required=True)


class ResCompany(models.Model):
    _inherit = "res.company"

    users_dc_notify = fields.Many2many("res.users", "compnay_user_dc_notif", "company_id", "user_id", "Liste des "
                  "personnes à nofitier lors de la création d'un dossier commercial")
    marge_level = fields.Float("Niveau min de marge applicable", default=20.0)
    marge_level_max = fields.Float("Niveau max de marge applicable", default=100.0)
    committee_setting_ids = fields.One2many("committee.setting", 'company_id', 'Paramétrage des commissions')