# -*- coding:utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import Warning, ValidationError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def convert_to_devise(self, amount, devise_from, device_to):
        for rec in self:
            amount_convert = amount
            if devise_from != device_to:
                amount_convert = rec.currency_id.with_context(date=rec.invoice_date).compute(amount,
                                                                                             rec.company_id.currency_id)
            return amount_convert

    @api.depends('invoice_line_ids.price_total')
    def _amount_all_currency(self):
        for inv in self:
            Taxes = False
            amount_untaxed_currency = amount_tax_currency = 0.0
            lines = inv.invoice_line_ids.filtered(lambda l: l.used_into_dc is True)
            amount_untaxed_currency = sum(line.price_subtotal for line in lines)
            for line in lines:
                currency = line.move_id and line.move_id.currency_id or None
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                l_taxes = line.tax_ids.compute_all(price, currency, line.quantity, product=line.product_id,
                                                   partner=line.move_id.partner_id)
                if l_taxes:
                    amount_tax_currency += sum(taxe['amount'] for taxe in l_taxes['taxes'])

            amount_total_currency = amount_untaxed_currency + amount_tax_currency
            sign = inv.move_type in ['in_refund', 'out_refund'] and -1 or 1
            inv.amount_untaxed_currency = inv.convert_to_devise(amount_untaxed_currency * sign, inv.currency_id,
                                                                inv.company_id.currency_id)
            inv.amount_tax_currency = inv.convert_to_devise(amount_tax_currency * sign, inv.currency_id,
                                                            inv.company_id.currency_id)
            inv.amount_total_currency = inv.convert_to_devise(amount_total_currency * sign, inv.currency_id,
                                                              inv.company_id.currency_id)

    amount_untaxed_currency = fields.Float(string='Montant HT en dévise', store=True, readonly=True,
                                           compute='_amount_all_currency',
                                           tracking=True)
    amount_tax_currency = fields.Float(string='Taxes en dévise', store=True, readonly=True,
                                       compute='_amount_all_currency')
    amount_total_currency = fields.Float(string='Montant total en dévise', store=True, readonly=True,
                                         compute='_amount_all_currency')
    type_neurone = fields.Selection([('interne', 'Interne'), ('externe', "Lié à un projet")], 'Type de facture',
                                    default='interne')
    dossier_id = fields.Many2one('neurones.dossier.manager', "Dossier commercial", required=False)


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    used_into_dc = fields.Boolean("Est pris en compte dans le total DC", default=True)
