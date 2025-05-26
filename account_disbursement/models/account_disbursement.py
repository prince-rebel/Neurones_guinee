# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime


class AccountDisbursementType(models.Model):
    _name = "account.disbursement.type"
    _description = "Disbursement type management"

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")


class AccountDisbursement(models.Model):
    _name = "account.disbursement"
    _description = "Disbursement management"

    def send_notification(self, email_template, context=None):
        template_id = self.env['ir.model.data']._xmlid_to_res_id(email_template)
        if template_id:
            try:
                template = self.env["mail.template"].browse(template_id)
                if template:
                    result = template.send_mail(res_id=self.id, force_send=True)
                    return True
            except:
                return False

    def _getAccountComptable(self):
        group_templ = self.env['ir.model.data']._xmlid_to_res_id('account.group_account_user')
        emails = ""
        if group_templ:
            group = self.env['res.groups'].search([('id', '=', group_templ)])
            if group:
                if group.users:
                    for user in group.users:
                        emails += user.login + ";"
        for dis in self:
            dis.account_emails = emails
        return

    def _getDirectionEmail(self):
        group_templ = self.env['ir.model.data']._xmlid_to_res_id(
            'account_disbursement.group_disbursement_account_manager')
        emails = ""
        if group_templ:
            group = self.env['res.groups'].search([('id', '=', group_templ)])
            if group:
                if group.users:
                    for user in group.users:
                        emails += user.login + ";"
        for dis in self:
            dis.direction_emails = emails
        return

    name = fields.Char("Référence", required=True, default="/")
    user_id = fields.Many2one("res.users", "Initiateur", required=True, default=lambda self: self.env.user.id)
    employee_id = fields.Many2one("hr.employee", "Bénéficiaire", required=False)
    user_employee_id = fields.Many2one('res.users', "Utilisateur lié à l'employé", related='employee_id.user_id',
                                       store=True)
    partner_id = fields.Many2one('res.partner', 'Parténaire', required=False)
    motif = fields.Text("Description", required=True)
    payment_mode = fields.Selection([('cash', "Espèce"), ('bank', 'Chèque')], default='cash')
    type = fields.Selection(
        [('transport', 'Transport'), ('commission', 'Commission commerciale'), ('Autres', 'Autres')], required=True)
    type_id = fields.Many2one('account.disbursement.type', 'Type', required=False)
    manager_id = fields.Many2one("res.users", "Manager", required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('manager', 'En cours de validation - Manager'),
                              ('dg', 'En cours de validatation - DG'), ('account', 'Comptable'), ('done', 'Validé'),
                              ('reject', 'Rejetté'),
                              ('cancel', 'Annulé')], default='draft')
    num_transaction = fields.Char("N° chèque/Bon de caisse")
    amount = fields.Float("Montant")
    date = fields.Date("Date de création", default=str(datetime.now())[:10])
    date_validation = fields.Date("Date de validation")
    account_emails = fields.Char("Mails des comptables", compute="_getAccountComptable")
    direction_emails = fields.Char("Mails des directeurs", compute="_getDirectionEmail")
    journal_id = fields.Many2one("account.journal", "Journal")
    statement_id = fields.Many2one("account.bank.statement", "Relévé", domain="[('journal_id', '=', journal_id)]")

    @api.model
    def create(self, vals):
        if vals.get('name', _('/')) == _('/'):
            vals['name'] = self.env['ir.sequence'].next_by_code('account.disbursement') or _('/')
        return super(AccountDisbursement, self).create(vals)

    @api.onchange('user_id')
    def onChangeUser(self):
        if self.user_id:
            employee = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)])
            if employee and employee.parent_id:
                self.manager_id = employee.parent_id.user_id

    def action_send_comptable(self):
        for dis in self:
            dis.state = "account"
            result = dis.send_notification("email_template_account_notif")

    def action_send_manager(self):
        for disb in self:
            res = disb.send_notification("email_template_manager_notif")
            disb.state = "manager"

    def action_submit_to_validation(self):
        for dis in self:
            if dis.type == 'transport':
                dis.action_send_comptable()
            else:
                dis.action_send_manager()

    def action_send_dg(self):
        for dis in self:
            dis.send_notification("email_template_dg_notif")
            dis.state = "dg"

    def action_done(self):
        for disb in self:
            # disb.send_notification("email_template_user_done_notif")
            disb.state = "done"
            disb.date_validation = fields.Datetime.now()
            val = {
                'date': disb.date,
                'name': disb.motif,
                'partner_id': disb.partner_id.id or False,
                'amount': -1 * disb.amount,
                'ref': disb.num_transaction,
                'statement_id': disb.statement_id.id or False
            }
            self.env['account.bank.statement.line'].create(val)

    def action_refused(self):
        for dis in self:
            dis.send_notification("email_template_user_refused_notif")
            dis.state = "reject"

    def action_cancel(self):
        self.state = "cancel"
