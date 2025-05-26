# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class Invoice(models.Model):
    _inherit = 'account.move'

    @api.depends('printing_type_invoice')
    def _getSaleOrder(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                order_obj = rec.env['sale.order']
                order = order_obj.search([('name', '=', rec.invoice_origin)])
                if order:
                    rec.order_id = order
                    rec.advance_payment_rate = (rec.amount_total / rec.order_id.amount_total) * 100
                    invoices = rec.order_id.filtered(lambda r: r.id == rec.id and r.state != 'cancel')
                    if invoices:
                        rec.total_accoumpte = sum([inv.amount_total for inv in invoices])
                    rec.amount_to_paid = rec.order_id.amount_total - (rec.total_accoumpte + rec.amount_total)
                return False
            else:
                rec.advance_payment_rate = 0.0
                rec.order_id = False

    def _getAdvancePaymentRate(self):
        order = self._getSaleOrder()
        if order:
            return (self.amount_total / order.amount_total) * 100

    # @api.onchange('printing_type_invoice')
    # def onChangePrintTypeVoice(self):
    #     if

    printing_type_invoice = fields.Selection([('normale', 'Facture normale'), ('acompte', 'Facture acompte'),
                                              ('sold', 'Facture soldée'), ('exonere', 'Exoneré de TVA'),
                                              ('exo_acompte', 'Acompte exonéré'), ('exo_solde', 'Solde exonéré')
                                              ], 'Type de facture à imprimer', index=True, readonly=False,
                                             default='normale')
    amount_tva_exone = fields.Integer("Montant de la TVA Exonéréé")
    order_id = fields.Many2one('sale.order', 'Bon de commande', required=False, compute='_getSaleOrder')
    advance_payment_rate = fields.Float('Taux acompte', compute='_getSaleOrder', digits=(16, 2))
    amount_to_paid = fields.Float('Montant TTC à payer', compute='_getSaleOrder')
    total_accoumpte = fields.Float('Montant TTC payé', compute='_getSaleOrder')
    amount_untaxed_sold = fields.Float('Montant HT Solde')
    amount_total_sold = fields.Float('Montant TTC Solde')

    #    taux_invoice = fields.Float("Taux montant", compute='_getSaleOrder')

    def invoice_print(self):
        for rec in self:
            rec.ensure_one()
            rec.sent = True
            return rec.env.ref('account.account_invoices').report_action(rec)
