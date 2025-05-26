# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
# from odoo.tools import Number_To_Word
from num2words import num2words
from itertools import groupby
import time
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        for rec in self:
            sale_orders = rec.env['sale.order'].browse(rec._context.get('active_ids', []))

            if rec.advance_payment_method == 'delivered':
                sale_orders._create_invoices()
            elif rec.advance_payment_method == 'all':
                sale_orders._create_invoices(final=True)
            else:
                # Create deposit product if necessary
                if not rec.product_id:
                    vals = rec._prepare_deposit_product()
                    rec.product_id = rec.env['product.product'].create(vals)
                    rec.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id',
                                                                    rec.product_id.id)

                sale_line_obj = rec.env['sale.order.line']
                for order in sale_orders:
                    if rec.advance_payment_method == 'percentage':
                        amount = order.amount_untaxed * rec.amount / 100
                    else:
                        amount = rec.amount
                    if rec.product_id.invoice_policy != 'order':
                        raise UserError(_(
                            'The product used to invoice a down payment should have an invoice policy set to "Ordered '
                            'quantities". Please update your deposit product to be able to create a deposit invoice.'))
                    if rec.product_id.type != 'service':
                        raise UserError(_(
                            "The product used to invoice a down payment should be of type 'Service'. Please use "
                            "another product or update this product."))
                    taxes = rec.product_id.taxes_id.filtered(
                        lambda r: not order.company_id or r.company_id == order.company_id)
                    if order.fiscal_position_id and taxes:
                        tax_ids = order.fiscal_position_id.map_tax(taxes).ids
                    else:
                        tax_ids = taxes.ids
                    so_line = sale_line_obj.create({
                        'name': _('Avance %s: %s') % ('du', time.strftime('%d-%m-%Y'),),
                        'price_unit': amount,
                        'product_uom_qty': 0.0,
                        'order_id': order.id,
                        'discount': 0.0,
                        'product_uom': rec.product_id.uom_id.id,
                        'product_id': rec.product_id.id,
                        'tax_id': [(6, 0, tax_ids)],
                        'is_downpayment': True,
                    })
                    rec._create_invoice(order, so_line, amount)
            if rec._context.get('open_invoices', False):
                return sale_orders.action_view_invoice()
            return {'type': 'ir.actions.act_window_close'}


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
        for rec in self:
            disc = 0
            for line in rec.invoice_line_ids:
                disc += line.price_subtotal * line.discount / 100
            rec.total_discount = disc

    @api.depends('amount_total')
    def _get_amount_to_letter(self):
        for rec in self:
            rec.write({'amount_letter': ""})
            if rec.amount_total:
                # rec.write({'amount_letter': ""})
                # try:
                #     rec.write({'amount_letter': Number_To_Word.Number_To_Word(rec.amount_total, 'fr',
                #                                                               rec.currency_id.currency_unit_label, '')})
                # except Exception as e:
                #     rec.write({'amount_letter': "Conversion error"})
                try:
                    rec.write({'amount_letter': num2words(rec.amount_total, lang='fr', to='currency', currency=rec.currency_id.currency_unit_label)})
                except Exception as e:
                    logging.error(f"Error converting amount to letter: {e}")
                    rec.write({'amount_letter': "Conversion error"})
            else:
                rec.write({'amount_letter': ""})

    total_discount = fields.Float(compute='_get_total_discount', string='Remise totale')
    amount_letter = fields.Char(compute='_get_amount_to_letter')
    mode_paiement = fields.Selection([
        ('cheque', 'Chèque'),
        ('espece', 'Espèce'),
        ('virement', 'Virement'),
    ], 'Mode de paiement', index=True, readonly=False)
    mode_payment = fields.Many2one('methode.payment', 'Mode de paiement')


class Sale(models.Model):
    _inherit = 'sale.order'

    def order_lines_layouted(self):
        for rec in self:
            super(Sale, rec).order_lines_layouted()
            """
            Returns this order lines classified by sale_layout_category and separated in
            pages according to the category pagebreaks. Used to render the report.
            """
            rec.ensure_one()
            report_pages = [[]]
            for category, lines in groupby(rec.order_line, lambda l: l.layout_category_id):
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

    def _get_total_discount(self):
        for rec in self:
            disc = 0
            for line in rec.invoice_line_ids:
                disc += line.price_subtotal * line.discount / 100
            rec.total_discount = disc

    @api.depends('amount_total')
    # def _get_amount_to_letter(self):
    #     for rec in self:
    #         rec.write({'amount_letter': ""})
    #         if rec.amount_total:
    #             rec.write({'amount_letter': Number_To_Word.Number_To_Word(rec.amount_total, 'fr',
    #                                                                       rec.currency_id.symbol, '')})
    def _get_amount_to_letter(self):
        for rec in self:
            rec.write({'amount_letter': ""})
            if rec.amount_total:
                try:
                    rec.write({'amount_letter': num2words(rec.amount_total, lang='fr', to='currency', currency=rec.currency_id.symbol)})
                except Exception as e:
                    logging.error(f"Error converting amount to letter: {e}")
                    rec.write({'amount_letter': "Conversion error"})

    def _getPaidDeposit(self):
        for order in self:
            amount = 0
            invoice_paids = order.invoice_ids.filtered(lambda inv: inv.state == 'paid')
            if invoice_paids:
                amount = sum([inv.amount_total for inv in invoice_paids])
            order.paid_deposit = amount

    amount_letter = fields.Char(compute='_get_amount_to_letter', default="", string="Montant (En lettre)")
    project = fields.Text('Projet')
    mode_paiement = fields.Selection([
        ('cheque', 'Chèque'),
        ('espece', 'Espèce'),
        ('virement', 'Virement'),
    ], 'Mode de paiement', index=True, readonly=False)
    mode_payment = fields.Many2one('methode.payment', 'Mode de paiement')
    garanty = fields.Selection([
        ('6m', '6 mois'),
        ('1an', '1 an'),
        ('2ans', '2 ans'),
        ('3ans', '3 ans'),
    ], 'Garantie', index=True, readonly=False)
    delay_validite = fields.Selection([
        ('15j', '15 Jours'),
        ('30j', '30 Jours'),
        ('60j', '60 Jours'),
        ('90j', '90 Jours'),
        ('120j', '120 Jours'),
    ], 'Validité', index=True, readonly=False)
    delai_livraison = fields.Char('Délai de livraison')
    paid_deposit = fields.Float('Acompte perçu', compute='_getPaidDeposit')


class Stock(models.Model):
    _inherit = 'stock.move'

    # move_lines = fields.One2many('stock.move', 'picking_id', string="Stock Moves", copy=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    serie_number = fields.Char("Numéro de série")


class MethodPayment(models.Model):
    _name = "methode.payment"
    _description = "Methode de payement"

    name = fields.Char('Mode de paiement')
