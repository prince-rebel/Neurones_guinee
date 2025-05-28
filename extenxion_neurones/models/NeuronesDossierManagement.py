# -*- coding:utf-8 -*-


from odoo import api, models, fields, _

import logging
_logger = logging.getLogger(__name__)


class NeuronesDossierManagement(models.Model):
    _name = "neurones.dossier.manager"
    _description = "Gestion des dossiers"

    def send_notification(self, email_id, context=None):
        self.ensure_one()
        template_id = self.env['ir.model.data'].get_object_reference('extenxion_neurones', email_id)
        try:
            mail_templ = self.env['mail.template'].browse(template_id[1])
            result = mail_templ.send_mail(res_id=self.id, force_send=True)
            return True
        except:
            return False

    @api.model
    def create(self, vals):
        date1 = vals['date']
        date2 = date1.strftime('%Y-%m-%d')
        d = date2[:10]
        # sequence_date = vals['date'][:10]
        # sequence = vals['date'][:10]
        if vals.get('name', _('/')) == _('/'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id'], ir_sequence_date=d, ir_sequence_date_range=d).\
                                   next_by_code('neurones.dossier.manager') or _('/')
            else:
                vals['name'] = self.env['ir.sequence'].with_context(ir_sequence_date=d, ir_sequence_date_range=d).\
                                   next_by_code('neurones.dossier.manager') or _('/')
        result = super(NeuronesDossierManagement, self).create(vals)
        return result

    def convert_to_devise(self, amount, devise_from, device_to):
        amount_convert = amount
        if devise_from != device_to:
            amount_convert = amount/devise_from.rate
        return amount_convert


    @api.depends('in_ids')
    def _compute_all_amount(self):
        for dossier in self:
            amount_in_prov = amount_in_def = amount_out_prov = amount_out_def = amount_decaissement = other_depense = 0.0
            if dossier.in_ids:
                amount_in_prov = sum([x.amount_untaxed_currency for x in dossier.in_ids])
            #                dossier.amount_business_provisoire = 0 #amount_in_prov
            if dossier.in_invoice_ids:
                amount_in_def = sum([x.amount_untaxed_currency for x in dossier.in_invoice_ids])
                amount_to_cash = amount_received = 0
                for x in dossier.in_invoice_ids:
                    to_pay = x.amount_residual
                    po_paid = x.amount_total - x.amount_residual
                    montant_paye = montant_a_paye = 0
                    if x.amount_tax:
                        perc = (x.amount_untaxed / x.amount_total)
                        montant_a_paye = to_pay * perc
                        montant_paye = po_paid * perc
                    amount_to_cash += self.convert_to_devise(montant_a_paye, x.currency_id, dossier.currency_id)
                    amount_received += self.convert_to_devise(montant_paye, x.currency_id, dossier.currency_id)
                    print(amount_received)
                dossier.amount_to_cash = amount_to_cash
                dossier.amount_received = amount_received
            else:
                dossier.amount_to_cash = 0
                dossier.amount_received = 0
            if dossier.out_ids:
                amount_out_prov = sum([x.amount_untaxed_currency for x in dossier.out_ids])
            if dossier.out_invoice_ids:
                amount_out_def = sum([x.amount_untaxed_currency for x in dossier.out_invoice_ids])
                amount_po_paid = amount_po_to_cash = 0
                for x in dossier.out_invoice_ids:
                    to_pay = x.amount_residual
                    po_paid = x.amount_total - x.amount_residual
                    montant_paye = montant_a_paye = 0
                    if x.amount_tax:
                        perc = (x.amount_untaxed / x.amount_total)
                        montant_a_paye = to_pay * perc
                        montant_paye = po_paid * perc
                    amount_po_to_cash += self.convert_to_devise(montant_a_paye, x.currency_id, dossier.currency_id)
                    amount_po_paid += self.convert_to_devise(montant_paye, x.currency_id, dossier.currency_id)
                dossier.amount_po_paid = amount_po_paid
                dossier.amount_po_to_cash = amount_po_to_cash
            else:
                dossier.amount_po_paid = 0
                dossier.amount_po_to_cash = 0
            if dossier.disbursement_ids:
                amount_decaissement = sum(
                    [x.amount for x in dossier.disbursement_ids.filtered(lambda d: d.state == 'done')])
            marge_prov = amount_in_prov - (amount_out_prov + sum([x.amount for x in dossier.disbursement_ids]))
            marge_def = amount_in_def - (amount_out_def + amount_decaissement)
            if amount_in_prov != 0:
                perc_marge_prov = (marge_prov / amount_in_prov) * 100
            else:
                perc_marge_prov = 0
            if amount_in_def != 0:
                perc_marge_def = (marge_def / amount_in_def) * 100
                dossier.amount_ca_definitive = amount_in_def
            else:
                perc_marge_def = 0
                dossier.amount_ca_definitive = 0
            if dossier.other_move_ids:
                other_depense = sum([x.amount_total_signed for x in dossier.other_move_ids])

            dossier.amount_business_provisoire = amount_in_prov
            # dossier.marge_previsionnelle = 0
            dossier.backlog = amount_in_prov - amount_in_def
            dossier.depense_provisoire = amount_out_prov
            dossier.depense_definitive = amount_out_def + amount_decaissement + other_depense
            dossier.marge_provisoire = marge_prov
            dossier.perc_marge_provisoire = perc_marge_prov
            dossier.marge_definitive = marge_def
            dossier.perc_marge_definitive = perc_marge_def
            dossier.other_depense = amount_decaissement

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

    def _compute_stock_depense(self):
        for dc in self:
            amount = 0
            m_lines = self.env['account.move.line'].search([('dossier_id', '=', dc.id)])
            print(m_lines)
            if m_lines:
                for line in m_lines:
                    l_balance = line.debit - line.credit
                    amount += l_balance
            print(amount)
            dc.depense_stock = amount

    def reload_initial_data(self):
        sale_order = self.env['sale.order'].search([('dossier_id', '=', self.id)], limit=1)
        if sale_order:
            amount = sale_order.convert_to_devise(sale_order.globale_marge, sale_order.currency_id,
                                                                     self.currency_id)
            _logger.warning("La marge previ est %s"%amount)
            vals = {
                'date': sale_order.date_order,
                'user_id': sale_order.env.user.id,
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

    def _get_out_move(self):
        journal_ids = self.env['account.journal'].search([('type', 'not in', ('sale', 'purchase'))]).ids
        if journal_ids:
            return [('journal_id', 'in', journal_ids), ('type_neurone', '=', 'externe')]
        else:
            return []

    name = fields.Char("Référence du dossier", required=True, default="/", readonly=True, store=True)
    ref_bc_customer = fields.Char("Référence bon de commande client", readonly=True, store=True)
    project_name = fields.Text("Nom du projet", store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Client', required=True, index=True, readonly=True, store=True)
    date = fields.Date("Date", required=True)
    date_creation = fields.Date("Date de création", required=True, readonly=True, store=True)
    date_end_project = fields.Date("Date fin projet", required=False)
    payment_term_id = fields.Many2one('account.payment.term', "Conditions de paiement", store=True)
    in_ids = fields.One2many('sale.order', 'dossier_id', "Bons de commande clients", required=False)
    sale_count = fields.Integer(string='# de BCs', compute='_get_all_count', readonly=True)
    in_invoice_ids = fields.One2many('account.move', 'dossier_id', "Factures clients", required=False,
                                     domain=[('type', 'in', ('out_invoice', 'out_refund'))])
    out_invoice_ids = fields.One2many('account.move', 'dossier_id', "Factures Fournisseurs", required=False,
                                      domain=[('type', 'in', ('in_invoice', 'in_refund'))])
    other_move_ids = fields.One2many('account.move', 'dossier_id', "Autres pieces a prendre en compte",
                                     domain=[('type', 'not in', ('in_invoice', 'in_refund', 'out_invoice', 'out_refund'))])
    invoice_count = fields.Integer(string='# de Factures clients', compute='_get_all_count', readonly=True)
    out_ids = fields.One2many('purchase.order', 'dossier_id', "Achats fournisseurs", required=False)
    disbursement_ids = fields.One2many("account.disbursement", "dossier_id", "Décaissements")
    disbursement_count = fields.Integer("N° decaissements", compute='_get_all_count')
    purchase_count = fields.Integer(string="# d'Achats", compute='_get_all_count', readonly=True)
    pinvoice_count = fields.Integer(string="# de Factures d'achats", compute='_get_all_count', readonly=True)
    amount_business_provisoire = fields.Float("CA provisoire", compute=_compute_all_amount)
    amount_ca_definitive = fields.Float("CA définitif", compute=_compute_all_amount)

    backlog = fields.Float("Backlog", compute='_compute_all_amount', store=False)
    depense_stock = fields.Float("Depenses Stock", compute='_compute_stock_depense', store=False)
    other_depense = fields.Float("Autres dépenses", compute=_compute_all_amount)
    depense_provisoire = fields.Float("Dépenses provisoires", compute=_compute_all_amount)
    depense_definitive = fields.Float("Dépenses Définitives", compute=_compute_all_amount)
    marge_provisoire = fields.Float("Marge provisoire", compute=_compute_all_amount)
    perc_marge_provisoire = fields.Float("% Marge provisoire", compute=_compute_all_amount)
    marge_definitive = fields.Float("Marge Définitive", compute=_compute_all_amount)
    perc_marge_definitive = fields.Float("% Marge Définitive", compute=_compute_all_amount)
    marge_previsionnelle = fields.Float("Marge Prévisionnelle", readonly=True,  store=True)
    perc_marge_previsionnelle = fields.Float("% Marge Prévisionnelle")
    user_id = fields.Many2one("res.users", "Responsable, ", required=True, readonly=True, store=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 readonly=True, store=True)
    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team,
                              oldname='section_id', readonly=True, store=True)
    state = fields.Selection([('draft', 'Brouillon'), ('confirmed', 'Confirmé'), ('done', 'Clôturé'), ('cancel', 'Annuler')],
                             default='draft', string="État")
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Dévise", readonly=True,
                                  required=True)
    amount_received = fields.Float("Montant payé", compute=_compute_all_amount)
    amount_to_cash = fields.Float("Montant à payer", compute=_compute_all_amount)
    amount_po_paid = fields.Float("Montant fournisseurs payés", compute=_compute_all_amount)
    amount_po_to_cash = fields.Float("Reste fournisseur à payer", compute=_compute_all_amount)
    saler_id = fields.Many2one("res.users", "Commercial(e)", required=False, readonly=True, store=True)
    employee_saler_id = fields.Many2one("hr.employee", 'Commercial(e)', required=False)
    av_saler_id = fields.Many2one('hr.employee', 'Avant-Vente', required=False)
    saler_manager_id = fields.Many2one('res.users', 'Manager des ventes', required=False)
    employee_saler_manager_id = fields.Many2one("hr.employee", "Commission Manager", required=False)
    committee_ids = fields.One2many("committee.sale.management", "dossier_id", "Les commissions commerciales")
    type_marge_id = fields.Many2one('type.marge_management', 'Type de marge', required=False, compute='_get_type_marge',
                                    store=False)
    rest_a_facture = fields.Boolean("Reste à facturer")
    reste_a_encaisser = fields.Boolean("Rester à encaisser")

    def _get_type_marge(self):
        type_marge_obj = self.env['type.marge_management']
        this_date = fields.Datetime.now()
        # print(this_date)
        marge = False
        for dc in self:
            type_marges = type_marge_obj.search([('marge_min', '<=', dc.perc_marge_definitive),
                                                 ('marge_max', '>=', dc.perc_marge_definitive)])
            if type_marges:
                for type_marge in type_marges:
                    if type_marge.date_end:
                        if dc.date >= type_marge.date_start and dc.date <= type_marge.date_end:
                            dc.type_marge_id = type_marge
                    else:
                        type_marges.search([('date_start', '<=', dc.date)], order='date_start desc', limit=1)
                        if type_marge:
                            dc.type_marge_id = type_marge
            else:
                dc.type_marge_id = False

    def _get_invoicing_infos(self):
        for dc in self:
            a_facture = 0
            e_encaisse = dc.amount_ca_definitive - dc.amount_received
            dc.rest_a_facture = False
            dc.reste_a_encaisser = False
            if dc.backlog != 0:
                dc.rest_a_facture = True
            if e_encaisse != 0:
                dc.reste_a_encaisser = True


class CommitteeSaleManagement(models.Model):
    _name = "committee.sale.management"
    _description = "Committee Sale Management"

    beneficiaire_id = fields.Many2one("hr.employee", "Bénéficiaire", required=False)
    committee_total = fields.Integer("Total commission")
    committee_paid = fields.Integer("Total commission payée")
    committee_payable = fields.Integer("Commission à payer")
    dossier_id = fields.Many2one("neurones.dossier.manager", "Dossier Commercial", required=True)
    date = fields.Datetime("Date", store=True)
    company_id = fields.Many2one('res.company', 'Société', related='dossier_id.company_id', store=True)
    project_name = fields.Text("Nom du projet", store=True, related="dossier_id.project_name")


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

