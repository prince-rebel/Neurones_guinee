# -*- coding:utf-8 -*-

from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)


class NeuronesDossierManagement(models.Model):
    _name = "neurones.dossier.manager"
    _description = "Gestion des dossiers"
    _order = 'id ASC'

    def send_notification(self, email_id, context=None):
        for dos in self:
            template_id = self.env['ir.model.data'].get_object_reference('extenxion_neurones', email_id)
            try:
                mail_templ = self.env['mail.template'].browse(template_id[1])
                result = mail_templ.send_mail(res_id=dos.id, force_send=True)
                return True
            except:
                return False

    @api.model
    def create(self, vals):
        sequence_date = vals['date'][:10] if 'date' in vals else ''
        if vals.get('name', _('/')) == _('/'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id'],
                                                                    ir_sequence_date=sequence_date,
                                                                    ir_sequence_date_range=sequence_date). \
                                   next_by_code('neurones.dossier.manager') or _('/')
            else:
                vals['name'] = self.env['ir.sequence'].with_context(ir_sequence_date=sequence_date,
                                                                    ir_sequence_date_range=sequence_date).next_by_code(
                    'neurones.dossier.manager') or _('/')
        result = super(NeuronesDossierManagement, self).create(vals)
        return result

    def convert_to_devise(self, amount, devise_from, device_to):
        for rec in self:
            amount_convert = amount
            if devise_from != device_to:
                amount_convert = rec.currency_id.with_context(date=rec.create_date).compute(amount,
                                                                                            rec.company_id.currency_id)
            return amount_convert

    @api.depends('in_ids')
    def _compute_all_amount(self):
        for dossier in self:
            true_customer_invoices = dossier.in_invoice_ids.filtered(lambda x: x.state in ('draft','posted'))
            true_supplier_invoices = dossier.out_invoice_ids.filtered(lambda x: x.state in ('draft','posted'))
            amount_in_prov = amount_in_def = amount_out_prov = amount_out_def = amount_decaissement = \
                amount_to_cash = amount_received = amount_po_paid = amount_po_to_cash = 0.0
            if dossier.in_ids:
                amount_in_prov = sum([x.amount_untaxed_currency for x in dossier.in_ids])
                _logger.info(f"{'='*50}>L57 {amount_in_prov}")
            if true_customer_invoices:
                amount_in_def = sum([x.amount_untaxed_currency for x in true_customer_invoices])
                amount_to_cash = amount_received = 0

                for x in true_customer_invoices:
                    to_pay = x.amount_residual
                    po_paid = x.amount_total - x.amount_residual
                    montant_paye = montant_a_paye = 0
                    perc = (x.amount_untaxed / x.amount_total) if x.amount_total else 0
                    # print(perc)
                    montant_a_paye = to_pay * perc
                    montant_paye = po_paid * perc
                    _logger.info(f"{'='*50}>L70 Montant a paye {montant_a_paye}")
                    _logger.info(f"{'='*50}>L71 Montant deja paye {montant_paye}")
                    amount_to_cash += x.convert_to_devise(montant_a_paye, x.currency_id, dossier.currency_id)
                    amount_received += x.convert_to_devise(montant_paye, x.currency_id, dossier.currency_id)
            if dossier.out_ids:
                amount_out_prov = sum([x.amount_untaxed_currency for x in dossier.out_ids])
            if true_supplier_invoices:
                amount_out_def = sum([x.amount_untaxed_currency for x in true_supplier_invoices])
                amount_po_paid = amount_po_to_cash = 0
                for x in true_supplier_invoices:
                    to_pay = x.amount_residual
                    po_paid = x.amount_total - x.amount_residual
                    perc = (x.amount_untaxed / x.amount_total) if x.amount_total else 0
                    # print(perc)
                    montant_a_paye = to_pay * perc
                    montant_paye = po_paid * perc
                    amount_po_to_cash += x.convert_to_devise(montant_a_paye, x.currency_id, dossier.currency_id)
                    amount_po_paid += x.convert_to_devise(montant_paye, x.currency_id, dossier.currency_id)
            if dossier.disbursement_ids:
                amount_decaissement = sum(
                    [x.amount for x in dossier.disbursement_ids.filtered(lambda d: d.state == 'done')])
            marge_prov = amount_in_prov - (amount_out_prov + amount_decaissement)

            marge_def = amount_in_def - (amount_out_def + amount_decaissement)
            if amount_in_prov != 0:
                perc_marge_prov = (marge_prov / amount_in_prov) * 100
            else:
                perc_marge_prov = 0
            if amount_in_def != 0:
                perc_marge_def = (marge_def / amount_in_def) * 100
            else:
                perc_marge_def = 0
            dossier.update({
                'amount_business_provisoire': amount_in_prov,
                'amount_ca_definitive': amount_in_def,
                'backlog': amount_in_prov - amount_in_def,
                'depense_provisoire': amount_out_prov,
                'depense_definitive': amount_out_def + amount_decaissement,
                'marge_provisoire': marge_prov,
                'perc_marge_provisoire': perc_marge_prov,
                'marge_definitive': marge_def,
                'perc_marge_definitive': perc_marge_def,
                'other_depense': amount_decaissement,
                'amount_to_cash': amount_to_cash,
                'amount_received': amount_received,
                'amount_po_paid': amount_po_paid,
                'amount_po_to_cash': amount_po_to_cash
            })

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    def _get_all_count(self):
        for dossier in self:
            dossier.update({
                'sale_count': len(dossier.in_ids),
                'invoice_count': len(dossier.in_invoice_ids),
                'purchase_count': len(dossier.out_ids),
                'pinvoice_count': len(dossier.out_invoice_ids),
                'disbursement_count': len(dossier.disbursement_ids)
            })

    @api.onchange('perc_marge_provisoire', 'perc_marge_definitive')
    def compute_diff_perc_mage(self):
        diff_marge = self.perc_marge_definitive - self.perc_marge_provisoire

    #        if diff_marge

    def _get_committee_paid(self, employee_id):
        if employee_id:
            depenses = self.env['account.disbursement'].search(
                [('employee_id', '=', employee_id), ('dossier_id', '=', self.id)])
            # print(depenses)
            if depenses:
                return sum([x.amount for x in depenses])
        return 0

    @api.onchange('in_invoice_ids')
    def compute_committee_sale(self):
        for dc in self:
            dc.committee_ids.unlink()
            marge = dc.marge_definitive
            perc_marge = dc.perc_marge_definitive
            # print(marge)
            # print(perc_marge)
            rate = 0.0
            if dc.perc_marge_definitive > dc.company_id.marge_level_max:
                marge = dc.marge_definitive * rate / 100
                # print(marge)
            res = []
            if perc_marge >= dc.company_id.marge_level:
                if dc.company_id.committee_setting_ids:
                    for committee_setting in dc.company_id.committee_setting_ids:
                        val = {}
                        committee_apply = committee_setting.line_ids.filtered(
                            lambda l: l.committee_rate_min <= perc_marge
                                      and l.committee_rate_max > perc_marge)
                        # print(committee_apply)
                        if committee_apply:
                            if committee_apply.committee_setting_id.code == "CM":
                                val['beneficiaire_id'] = dc.employee_saler_id.id if dc.employee_saler_id else False
                            elif committee_apply.committee_setting_id.code == "AV":
                                val['beneficiaire_id'] = dc.av_saler_id.id if dc.av_saler_id else False
                            else:
                                val[
                                    'beneficiaire_id'] = dc.employee_saler_manager_id.id if dc.employee_saler_manager_id else False
                            committee = marge * committee_apply.rate / 100
                            val['committee_total'] = committee
                            val['committee_paid'] = dc._get_committee_paid(val['beneficiaire_id'])
                            val['committee_payable'] = val['committee_total'] - val['committee_paid']
                        res.append(val)

                        # print("%s - %s" %(committee_apply.name, committee_apply.rate))
            dc.committee_ids = res

    def reload_initial_data(self):
        sale_order = self.env['sale.order'].search([('dossier_id', '=', self.id)], limit=1)
        if sale_order:
            vals = {
                'date': sale_order.effective_date,
                'user_id': self.create_uid.id,
                'partner_id': sale_order.partner_id.id,
                'team_id': sale_order.team_id.id,
                'company_id': sale_order.company_id.id,
                'payment_term_id': sale_order.payment_term_id.id,
                'ref_bc_customer': sale_order.name,
                'marge_previsionnelle': sale_order.convert_to_devise(sale_order.globale_marge, sale_order.currency_id,
                                                                     self.currency_id),
                'perc_marge_previsionnelle': sale_order.taux_marge,
                'saler_id': sale_order.user_id.id,
                'saler_manager_id': sale_order.team_id.user_id.id,
                'project_name': sale_order.project,
            }
            self.write(vals)

    def _get_employee(self):
        emp_obj = self.env['hr.employee']
        for dc in self:
            if dc.saler_id:
                employee = emp_obj.search([('user_id', '=', dc.saler_id.id)])
                if employee:
                    dc.employee_saler_id = employee
            if dc.saler_manager_id:
                employee = emp_obj.search([('user_id', '=', dc.saler_manager_id.id)])
                if employee:
                    dc.employee_saler_manager_id = employee

    def _get_type_marge(self):
        type_marge_obj = self.env['type.marge_management']
        this_date = fields.Datetime.now()
        # print(this_date)
        marge = False
        for dc in self:
            type_marges = type_marge_obj.search([('marge_min', '<=', dc.perc_marge_definitive),
                                                 ('marge_max', '>=', dc.perc_marge_definitive)])
            dc.type_marge_id = False
            if type_marges:
                for type_marge in type_marges:
                    if type_marge.date_end:
                        if type_marge.date_start <= dc.date <= type_marge.date_end:
                            dc.type_marge_id = type_marge
                    else:
                        type_marges.search([('date_start', '<=', dc.date)], order='date_start desc', limit=1)
                        if type_marge:
                            _logger.info(f"{'=' * 50}>L229 {type_marge}")
                            dc.type_marge_id = type_marge

        #            #print(type_marge)
        # TODO : finaliser la fonction qui permet de récuperer automatiquement le type de marge des Dossiers Commerciaux
        return False

    # def _get_invoicing_infos(self):
    #     # TODO : finaliser la fonction qui permet d'avoir les informations sur les factures(Reste à facturer et reste à encaisser)
    #     for dc in self:
    #         a_facture = 0
    #         e_encaisse = dc.amount_ca_definitive - dc.amount_received
    #         if dc.backlog != 0:
    #             dc.rest_a_facture = True
    #         if e_encaisse != 0:
    #             dc.reste_a_encaisser = True
    #
    #     return True

    def _get_invoicing_infos(self):
        # TODO : finaliser la fonction qui permet d'avoir les informations sur les factures(Reste à facturer et reste à encaisser)
        for dc in self:
            dc.rest_a_facture = dc.backlog != 0
            dc.reste_a_encaisser = (dc.amount_ca_definitive - dc.amount_received) != 0
        return True

    name = fields.Char("Référence du dossier", required=True, default="/")
    ref_bc_customer = fields.Char("Référence bon de commande client")
    project_name = fields.Text("Nom du projet")
    partner_id = fields.Many2one('res.partner', 'Client', required=True, index=True)
    date = fields.Datetime("Date", required=False)
    date_creation = fields.Date("Date de création", required=True)
    date_end_project = fields.Date("Date fin projet", required=False)
    payment_term_id = fields.Many2one('account.payment.term', "Conditions de paiement", store=False)
    in_ids = fields.One2many('sale.order', 'dossier_id', "Bons de commande clients", required=False)
    sale_count = fields.Integer(string='# de BCs', compute='_get_all_count', readonly=True)
    in_invoice_ids = fields.One2many('account.move', 'dossier_id', "Factures clients", required=False,
                                     domain=[('move_type', '=', 'out_invoice')])
    invoice_count = fields.Integer(string='# de Factures clients', compute='_get_all_count', readonly=True)
    out_ids = fields.One2many('purchase.order', 'dossier_id', "Achats fournisseurs", required=False)
    disbursement_ids = fields.One2many("account.disbursement", "dossier_id", "Décaissements")
    disbursement_count = fields.Integer("N° decaissements", compute='_get_all_count')
    purchase_count = fields.Integer(string="# d'Achats", compute='_get_all_count', readonly=True)
    out_invoice_ids = fields.One2many('account.move', 'dossier_id', "Factures Fournisseurs", required=False,
                                      domain=[('move_type', '=', 'in_invoice')])
    pinvoice_count = fields.Integer(string="# de Factures d'achats", compute='_get_all_count', readonly=True)
    amount_business_provisoire = fields.Float("CA provisoire", compute=_compute_all_amount, store=False)
    amount_ca_definitive = fields.Float("CA définitif", compute='_compute_all_amount', store=False)
    backlog = fields.Float("Backlog", compute='_compute_all_amount', store=False)
    other_depense = fields.Float("Autres dépenses", compute=_compute_all_amount, store=False)
    depense_provisoire = fields.Float("Dépenses provisoires", compute=_compute_all_amount, store=False)
    depense_definitive = fields.Float("Dépenses Définitives", compute=_compute_all_amount, store=False)
    marge_provisoire = fields.Float("Marge provisoire", compute=_compute_all_amount, store=False)
    perc_marge_provisoire = fields.Float("% Marge provisoire", compute=_compute_all_amount, store=False)
    marge_definitive = fields.Float("Marge Définitive", compute='_compute_all_amount', store=False)
    marge_previsionnelle = fields.Float("Marge Prévisionnelle")
    perc_marge_previsionnelle = fields.Float("% Marge Prévisionnelle")
    perc_marge_definitive = fields.Float("% Marge Définitive", compute='_compute_all_amount', store=False)
    diff_perc_marge = fields.Float("Différence entre marge")
    user_id = fields.Many2one("res.users", "Responsable", required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'))
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team)
    state = fields.Selection(
        [('draft', 'Brouillon'), ('confirmed', 'Confirmé'), ('done', 'Clôturé'), ('cancel', 'Annuler')],
        default='draft', string="État")
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Dévise", readonly=True,
                                  required=True)
    amount_received = fields.Float("Montant payé", compute=_compute_all_amount, store=False)
    amount_to_cash = fields.Float("Montant facturé à payer", compute=_compute_all_amount, store=False)
    amount_po_paid = fields.Float("Montant fournisseurs payés", compute=_compute_all_amount, store=False)
    amount_po_to_cash = fields.Float("Reste fournisseur à payer", compute=_compute_all_amount, store=False)
    saler_id = fields.Many2one("res.users", "Commercial(e)", required=False)
    employee_saler_id = fields.Many2one("hr.employee", 'Commercial(e)', required=False)
    av_saler_id = fields.Many2one('hr.employee', 'Avant-Vente', required=False)
    saler_manager_id = fields.Many2one('res.users', 'Manager des ventes', required=False)
    employee_saler_manager_id = fields.Many2one("hr.employee", "Commission Manager", required=False)
    committee_ids = fields.One2many("committee.sale.management", "dossier_id", "Les commissions commerciales")
    type_marge_id = fields.Many2one('type.marge_management', 'Type de marge', required=False, compute='_get_type_marge',
                                    store=False)
    rest_a_facture = fields.Boolean("Reste à facturer", compute="_get_invoicing_infos", store=False)
    reste_a_encaisser = fields.Boolean("Rester à encaisser", compute="_get_invoicing_infos", store=False)


class CommitteeSaleManagement(models.Model):
    _name = "committee.sale.management"
    _description = "Committee Sale Management"

    beneficiaire_id = fields.Many2one("hr.employee", "Bénéficiaire", required=False)
    committee_total = fields.Integer("Total commission")
    committee_paid = fields.Integer("Total commission payée")
    committee_payable = fields.Integer("Commission à payer")
    dossier_id = fields.Many2one("neurones.dossier.manager", "Dossier Commercial", required=True)
    date = fields.Datetime("Date", related='dossier_id.date', store=True)
    company_id = fields.Many2one('res.company', 'Société', related='dossier_id.company_id', store=True)
    project_name = fields.Text("Nom du projet", related="dossier_id.project_name", store=True)


class TypeMargeManagement(models.Model):
    _name = "type.marge_management"
    _description = "gestion des marges"

    name = fields.Char("Désignation", required=True)
    marge_min = fields.Float("Marge Min")
    marge_max = fields.Float("Marge max")
    description = fields.Text("Description")
    active = fields.Boolean("Actif(ve)", default=True)
    company_id = fields.Many2one("res.company", "Société", required=False)
    date_start = fields.Date("Date de début", required=True)
    date_end = fields.Date("Date de fin")
