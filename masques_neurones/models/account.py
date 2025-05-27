# -*- coding: utf-8 -*-
from odoo import api,fields, models, _
from odoo.exceptions import UserError, ValidationError


class Invoice(models.Model):
    _inherit = 'account.move'

    @api.model
    @api.depends('invoice_origin')
    def _getSaleOrder(self):
        for rec in self:
            if rec.move_type  == 'out_invoice':
                order_obj = self.env['sale.order']
                order = order_obj.search([('name', '=', rec.invoice_origin)])
                if order:
                    rec.order_id = order
                    rate = (rec.amount_total/rec.order_id.amount_total)*100
                    rec.advance_payment_rate = rate if rate else 0
                    invoices = rec.order_id.filtered(lambda r: r.id == rec.id and r.state!= 'cancel')
                    if invoices:
                        rec.total_accoumpte = sum([inv.amount_total for inv in invoices])
                    if rec.total_accoumpte:
                        rec.amount_to_paid = rec.order_id.amount_total - (rec.total_accoumpte + rec.amount_total)
                    else:
                        rec.amount_to_paid = rec.order_id.amount_total - rec.amount_total

    def _getAdvancePaymentRate(self):
        order = self._getSaleOrder()
        print(order)
        if order:
            return (self.amount_total / order.amount_total) * 100

    printing_type_invoice = fields.Selection([
        ('normale', 'Facture normale'),
        ('acompte', 'Facture acompte'),
        ('sold', 'Facture soldée'),
        ('exonere', 'Exoneré de TVA'),
        ('exo_acompte', 'Acompte exonéré'),
        ('exo_solde','Solde exonéré')
       ], 'Type de facture à imprimer', select=True, readonly=False, default='normale')
    amount_tva_exone = fields.Integer("Montant de la TVA Exonéréé")
    order_id = fields.Many2one('sale.order', 'Bon de commande', store=True, required=False, compute='_getSaleOrder')
    advance_payment_rate = fields.Float('Taux acompte', store=True, readonly=True, copy=False, compute='_getSaleOrder', digits=(16, 2))
    amount_to_paid = fields.Float('Montant TTC à payer', store=True, compute='_getSaleOrder')
    total_accoumpte = fields.Float('Montant TTC payé', store=True, compute='_getSaleOrder')
    amount_untaxed_sold = fields.Float('Montant HT Solde')
    amount_total_sold = fields.Float('Montant TTC Solde')
    amount_advance_payment = fields.Float('Montant Acompte')
