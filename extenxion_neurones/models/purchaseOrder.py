# -*- coding:utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import Warning, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def convert_to_devise(self, amount, devise_from, device_to):
        for rec in self:
            amount_convert = amount
            if devise_from != device_to:
                amount_convert = rec.currency_id.with_context(date=rec.create_date).compute(amount,
                                                                                            rec.company_id.currency_id)
            return amount_convert

    @api.depends('order_line.price_total')
    def _amount_all_currency(self):
        for order in self:
            amount_untaxed_currency = amount_tax_currency = 0.0
            for line in order.order_line.filtered(lambda x: x.used_into_dc is True):
                amount_untaxed_currency += line.price_subtotal
                amount_tax_currency += line.price_tax
            amount_untaxed_currency = order.convert_to_devise(amount_untaxed_currency, order.currency_id, order.company_id.currency_id)
            amount_tax_currency = order.convert_to_devise(amount_tax_currency, order.currency_id, order.company_id.currency_id)
            print(amount_untaxed_currency)
            order.update({
                'amount_untaxed_currency': order.company_id.currency_id.round(amount_untaxed_currency),
                'amount_tax_currency': order.company_id.currency_id.round(amount_tax_currency),
                'amount_total_currency': amount_untaxed_currency + amount_tax_currency,
            })

    type_neurone = fields.Selection([('interne', 'Interne'), ('externe', "Lié à un projet")], 'Type de facture',
                                    default='externe')
    dossier_id = fields.Many2one('neurones.dossier.manager', "Dossier", required=False)
    amount_untaxed_currency = fields.Float(string='Montant HT en dévise', store=True, readonly=True, compute='_amount_all_currency',
                                     tracking=True)
    amount_tax_currency = fields.Float(string='Taxes en dévise', store=True, readonly=True, compute='_amount_all_currency')
    amount_total_currency = fields.Float(string='Montant total en dévise', store=True, readonly=True, compute='_amount_all_currency')

    # sector_activity_id = fields.Many2one('res.partner.sector_activity', 'Sectuer d\'activité',
    #                                      related='partner_id.sector_activity_id', store=True)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    used_into_dc = fields.Boolean("Est pris en compte dans le total DC", default=True)