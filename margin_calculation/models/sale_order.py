from odoo import api, fields, models  # alphabetically ordered
from odoo.exceptions import UserError


class PurchaseDiscout(models.Model):
    _name = "sale.purchase.discout"
    _description = "Remise produit"

    name = fields.Char(string="Nom", required=True)
    taux = fields.Float(string="Taux de la remise(%)", required=True)
    description = fields.Text(string="Description")


class FraisApproche(models.Model):
    _name = "sale.frais.approche"
    _description = "Frais d'approche"

    name = fields.Char(string="Nom", required=True)
    taux = fields.Float(string="Taux Frais d'approche(%)", required=True)
    description = fields.Text(string="Description")


class MargeVoulue(models.Model):
    _name = "sale.marge.voulue"
    _description = "Marge voulue"

    name = fields.Char(string="Nom", required=True)
    taux = fields.Float(string="Taux de la marge voulue(%)", required=True)
    description = fields.Text(string="Description")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("order_line.product_uom_qty", "order_line.marge_voulue_id")
    def _compute_globale_marge(self):
        for rec in self:
            order_line = rec.order_line
            if order_line:
                for line in order_line:
                    if line.amount_marge_voulue and line.amount_marge_voulue != 0.0 and line.amount_marge_voulue != '0.0':
                        rec.globale_marge += line.amount_marge_voulue

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.price_total', 'provision')
    def _compute_marging(self):
        for order in self:
            total_purchase = order.provision
            total_marge = 0.0
            frais_approche = 0.0
            for line in order.order_line:
                total_purchase += line.prix_revient_product * line.product_uom_qty
                total_marge += line.amount_marge_real
                frais_approche += line.amount_frais_approche
            order.update({
                'globale_marge': order.amount_untaxed - total_purchase,
                'amount_total_price_purchase': total_purchase,
                'frais_approche': frais_approche,
            })
            if order.amount_untaxed != 0:
                order.update({'taux_marge': ((order.amount_untaxed - total_purchase) / order.amount_untaxed) * 100})

    globale_marge = fields.Monetary(string="Amount Marge globale", store=True, readonly=True,
                                    compute='_compute_marging',
                                    tracking=True)
    taux_marge = fields.Float("TAUX DE MARGE", store=True, readonly=True, compute='_compute_marging',
                              tracking=True)
    amount_total_price_purchase = fields.Monetary('PRIX DE REVIENT', store=True, readonly=True,
                                                  compute='_compute_marging',
                                                  tracking=True)
    provision = fields.Monetary('Provision', tracking=True)
    frais_approche = fields.Monetary("Frais d'approche", compute='_compute_marging', tracking=True,
                                     store=True)
    purchase_order_count = fields.Integer("Purchase order count")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('price_purchase_fournisseur', 'discount_supplier', 'frais_approche_prec', 'marge_sale',
                  'marge_voulue_id', 'device_purchase_id')
    @api.depends('price_purchase_fournisseur', 'discount_supplier', 'frais_approche_prec', 'marge_sale',
                 'marge_voulue_id', 'device_purchase_id')
    def compute_prix_product_revient(self):
        if self.device_purchase_id:
            prix_purchase = (self.price_purchase_fournisseur * (
                    1 - self.discount_supplier / 100)) / self.device_purchase_id.rate
            prix_revient = ((self.price_purchase_fournisseur * (1 - self.discount_supplier / 100)) * (
                    1 + self.frais_approche_prec / 100)) / self.device_purchase_id.rate
            self.prix_revient_product = prix_revient
            self.amount_frais_approche = (prix_revient - prix_purchase) * self.product_uom_qty
        # amount_marge_voulue
        if self.marge_sale > 0:
            self.price_unit = self.prix_revient_product / (1 - self.marge_sale / 100)
        self.amount_marge_real = self.price_subtotal - (self.product_uom_qty * self.prix_revient_product)
        self.amount_marge_voulue = (self.product_uom_qty * self.prix_revient_product) * (
                self.marge_voulue_id.taux / 100)
        if (self.price_subtotal):
            self.taux_marge_real = (self.amount_marge_real / self.price_subtotal)

    @api.onchange('product_uom', 'product_uom_qty')
    def _compute_pricelist_item_id(self):
        super(SaleOrderLine, self)._compute_pricelist_item_id()
        self.compute_prix_product_revient()

    def _get_marge(self):
        for line in self:
            line.amount_marge_real = line.price_subtotal - (line.product_uom_qty * line.prix_revient_product)
            if (line.price_subtotal):
                line.taux_marge_real = (line.amount_marge_real / line.price_subtotal)

    price_purchase_fournisseur = fields.Float(string='Prix d\'achat fournisseur')
    device_purchase_id = fields.Many2one('res.currency', 'Déevise Achat', required=True)
    purchase_discout_id = fields.Many2one('sale.purchase.discout', 'Remise Fournisseur')
    discount_supplier = fields.Integer('Remise Fournisseur (%)')
    frais_approche_id = fields.Many2one('sale.frais.approche', 'Frais approche')
    frais_approche_prec = fields.Float("Frais d'approche (%))", default=0.0)
    amount_frais_approche = fields.Float("Montant frais d'approche")
    prix_revient_product = fields.Float("Prix de Revient", digits=(12, 0))
    marge_sale = fields.Float('Marge (%)')
    marge_voulue_id = fields.Many2one('sale.marge.voulue', 'Marge voulue')
    amount_marge_voulue = fields.Float('Montant Marge voulue', digits=(12, 0))
    taux_marge_real = fields.Float('Marge Brute Réelle', digits=(12, 0))
    amount_marge_real = fields.Float('Montant Marge Brute', digits=(12, 0))
