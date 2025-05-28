#-*- coding:utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words
from itertools import groupby
import time
from odoo.exceptions import UserError


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _prepare_so_line(self, order, analytic_tag_ids, tax_ids, amount):
        context = {'lang': order.partner_id.lang}
        so_values = {
            'name': _('Avance %s: %s') % ('du', time.strftime('%d-%m-%Y'),),
            'price_unit': amount,
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'discount': 0.0,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_tag_ids': analytic_tag_ids,
            'tax_id': [(6, 0, tax_ids)],
            'is_downpayment': True,
        }
        del context
        return so_values


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    reference = fields.Char('Référence')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    reference = fields.Char('Référence')


class Purchase(models.Model):
    _inherit = 'purchase.order'


class Invoice(models.Model):
    _inherit = 'account.move'

    def _get_total_discount(self):
        disc = 0
        for line in self.invoice_line_ids:
            disc += line.price_subtotal * line.discount / 100
        self.total_discount = disc

    @api.depends('amount_total')
    @api.model
    def _get_amount_to_letter(self):
        for rec in self:
            amount_text = num2words(rec.amount_total, lang='fr')
            rec.amount_letter = amount_text

    total_discount = fields.Float(compute='_get_total_discount', store=True, string='Remise totale')
    amount_letter = fields.Char(compute='_get_amount_to_letter', store=True)
    mode_paiement = fields.Selection([
        ('cheque', 'Chèque'),
        ('espece', 'Espèce'),
        ('virement', 'Virement'),
    ], 'Mode de paiement', select=True, readonly=False,required=False)
    mode_payment = fields.Many2one('methode.payment', 'Mode de paiement')


class Sale(models.Model):
    _inherit = 'sale.order'

    def _get_total_discount(self):
        disc = 0
        for line in self.invoice_line_ids:
            disc += line.price_subtotal * line.discount / 100
        self.total_discount = disc

    @api.depends('amount_total')
    def _get_amount_to_letter(self):
        for rec in self:
            if rec.amount_total:
                amount_text = num2words(rec.amount_total, lang='fr')
                print(amount_text)
                rec.amount_letter = amount_text

    def _getPaidDeposit(self):
        for order in self:
            amount = 0
            invoice_paids= order.invoice_ids.filtered(lambda inv: inv.state == 'paid')
            if invoice_paids:
                amount = sum([inv.amount_total for inv in invoice_paids])
            order.paid_deposit = amount

    amount_letter = fields.Char(compute='_get_amount_to_letter', store=True)
    project = fields.Text('Projet')
    mode_paiement = fields.Selection([
        ('cheque', 'Chèque'),
        ('espece', 'Espèce'),
        ('virement', 'Virement'),
    ], 'Mode de paiement', select=True, readonly=False)
    mode_payment = fields.Many2one('methode.payment','Mode de paiement')
    garanty = fields.Selection([
        ('6m', '6 mois'),
        ('1an', '1 an'),
        ('2ans', '2 ans'),
        ('3ans', '3 ans'),
    ], 'Garantie', select=True, readonly=False)
    delay_validite = fields.Selection([
        ('15j', '15 Jours'),
        ('30j', '30 Jours'),
        ('60j', '60 Jours'),
        ('90j', '90 Jours'),
        ('120j', '120 Jours'),
    ], 'Validité', select=True, readonly=False)
    delai_livraison= fields.Char('Délai de livraison')
    paid_deposit= fields.Float('Acompte perçu', compute='_getPaidDeposit')
    
    def order_lines_layouted(self):
        # super(Sale, self).order_lines_layouted()
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        for category, lines in groupby(self.order_line, lambda l: l.layout_category_id):
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page
            report_pages[-1].append({
                'name': category and category.name or 'Sans catégorie',
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'lines': list(lines)
            })

        return report_pages

class Stock(models.Model):
    _inherit = 'stock.picking'


class StockMove(models.Model):
    _inherit = 'stock.move'

    serie_number = fields.Char("Numéro de série")


class MethodPayment(models.Model):
    _name = "methode.payment"

    name = fields.Char('Mode de paiement')


class Company(models.Model):
    _inherit = 'res.company'

    fax = fields.Char("Fax")
    n_cc = fields.Char("N°CC")
    n_ifu = fields.Char("N°IFU")
    regime_imposition = fields.Char("Régime d’imposition")
    centre_impot = fields.Char("Centre des Impôts")