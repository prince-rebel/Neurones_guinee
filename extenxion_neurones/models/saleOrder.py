# -*- coding:utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import Warning, ValidationError


class SaleOrderSource(models.Model):
    _name = "sale.order.source"
    _description = "Source de provenance"

    name = fields.Char("Libellé", required=True)
    description = fields.Text("Description")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_generate_dossier(self):
        self.ensure_one()
        if self.date_order:
            vals = {
                'date_creation': fields.Datetime.now(),
                'date': self.date_order,
                'user_id': self.env.user.id,
                'partner_id': self.partner_id.id,
                'team_id': self.team_id.id,
                'company_id': self.company_id.id,
                'payment_term_id': self.payment_term_id.id,
                'ref_bc_customer': self.name,
                'marge_previsionnelle': self.globale_marge,
                'perc_marge_previsionnelle': self.taux_marge,
                'project_name': self.project
            }
            dossier_id = self.env['neurones.dossier.manager'].create(vals)
            if dossier_id:
                dossier_id.send_notification('email_template_notify_dc')
                marge_provisoire = dossier_id.convert_to_devise(self.globale_marge, self.currency_id, dossier_id.currency_id)
                dossier_id.marge_provisoire = marge_provisoire
                self.dossier_id = dossier_id
            else:
                raise ValidationError(_("Erreur lors de la création du dossier."))
        else:
            raise ValidationError(_("Seuls les devis confirmés peuvent être utilisés pour générer les Dossiers commerciaux"))

    def convert_to_devise(self, amount, devise_from, device_to):
        for rec in self:
            amount_convert = amount
            if devise_from != device_to:
                amount_convert = rec.currency_id.with_context(date=rec.create_date).compute(amount, rec.company_id.currency_id)
            return amount_convert

    @api.depends('order_line.price_total')
    def _amount_all_currency(self):
        for order in self:
#            curreny_to_id = order.compzny_id.currency_id
            amount_untaxed_currency = amount_tax_currency = 0.0
            for line in order.order_line:
                amount_untaxed_currency += line.price_subtotal
                amount_tax_currency += line.price_tax
            amount_untaxed_currency = self.convert_to_devise(amount_untaxed_currency, order.currency_id,
                                                             order.company_id.currency_id)
            amount_tax_currency = self.convert_to_devise(amount_tax_currency, order.currency_id,
                                                         order.company_id.currency_id)
            print(amount_untaxed_currency)
            order.update({
                'amount_untaxed_currency': order.company_id.currency_id.round(amount_untaxed_currency),
                'amount_tax_currency': order.company_id.currency_id.round(amount_tax_currency),
                'amount_total_currency': amount_untaxed_currency + amount_tax_currency,
            })
    amount_untaxed_currency = fields.Float(string='Montant HT en dévise', store=False, readonly=True,
                                           compute='_amount_all_currency',
                                           track_visibility='always')
    amount_tax_currency = fields.Float(string='Taxes en dévise', store=False, readonly=True,
                                       compute='_amount_all_currency')
    amount_total_currency = fields.Float(string='Montant total en dévise', store=False, readonly=True,
                                         compute='_amount_all_currency')
    dossier_id = fields.Many2one('neurones.dossier.manager', "Dossier", required=False)
    sector_activity_id = fields.Many2one('res.partner.industry', 'Sectuer d\'activité',
                                        related='partner_id.industry_id', store=True)
    source_id = fields.Many2one('sale.order.source', 'Provenance', required=False)
