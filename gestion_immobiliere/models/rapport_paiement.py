from odoo import models, fields, api, tools, exceptions, _
from datetime import datetime, timedelta

from datetime import datetime, timedelta

from odoo.addons import decimal_precision as dp
import logging


# Heritage Vente/Quittance
class Quittance(models.Model):
    _inherit = 'sale.order'


class Quittance_suite_suite(models.Model):
    _inherit = 'sale.order'

    contrat_t = fields.Many2one('lb.paiement_location', string="Contrat")

    contrat_v = fields.Many2one('lb.contrat_vente', string="Contrat")

    type_bien = fields.Selection([
        ('consu', 'bien à vendre'),
        ('service', 'Bien à louer')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.', related='product_id.type')


class Quittance_suite(models.Model):
    _inherit = 'sale.order'

    contrat = fields.Many2one('lb.location', string="Contrat")

    contrat_id = fields.Char(string="Ref contrat")

    _sql_constraints = [
        ('non_contrat_unique',
         'UNIQUE(contrat_id)',
         "Vous avez déjà créé une facture de vente pour ce contrat"),
    ]

    type = fields.Selection([
        ('consu', 'bien à vendre'),
        ('service', 'Bien à louer')], required="True", related='product_id.type')

    # order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)

    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    partner_id = fields.Many2one('res.partner', string='Acheteur',
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                 change_default=True, index=True, track_visibility='always', track_sequence=1)

    product_id = fields.Many2one('product.product')


class order_line(models.Model):
    _inherit = 'sale.order.line'


class facture(models.Model):
    _inherit = 'account.invoice'

    type_bien = fields.Selection([
        ('consu', 'bien à vendre'),
        ('service', 'Bien à louer')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.', related='invoice_line_ids.type_bien')

    # partner_id = fields.Many2one('res.partner', string='Acheteur', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, change_default=True, index=True, track_visibility='always', track_sequence=1)

    mois_payee_c = fields.Selection([('janvier', 'Janvier'),
                                     ('fevrier', 'Février'),
                                     ('mars', 'Mars'),
                                     ('avril', 'Avril'),
                                     ('mai', 'Mai'),
                                     ('juin', 'Juin'),
                                     ('juillet', 'Juillet'),
                                     ('aout', 'Août'),
                                     ('septembre', 'Septembre'),
                                     ('octobre', 'Octobre'),
                                     ('novembre', 'Novembre'),
                                     ('decembre', 'Décembre')],
                                    string="paiement du mois")

    customer = fields.Boolean(related='partner_id.customer')

    supplier = fields.Boolean(related='partner_id.supplier')

    agent = fields.Boolean(related='partner_id.agent')


class facture_suite(models.Model):
    _inherit = 'account.invoice'

    product = fields.Many2one('product.product', related="invoice_line_ids.product_id")

    customer = fields.Boolean(related='partner_id.customer')
    supplier = fields.Boolean(related='partner_id.supplier')


class facture_suite_suite(models.Model):
    _inherit = 'account.invoice'

    contrat = fields.Many2one('lb.location', string="Contrat")
    
class facture_statut_agent(models.Model):
    _inherit = 'account.invoice'
    
    statut_agent = fields.Selection(
        [('bailleur', 'Est un bailleur'), ('courtier', 'Est un courtier')],
        string="Statut", related='partner_id.statut_agent', default='bailleur')  



class facture_contrat_t(models.Model):
    _inherit = 'account.invoice'


    contrat_t = fields.Many2one('lb.paiement_location', string="Contrat")
    
    contrat_v = fields.Many2one('lb.contrat_vente', string="Contrat")
    
    product_id = fields.Many2one('product.product')

class order_uite(models.Model):
    _inherit = 'account.invoice.line'

    bailleur_id = fields.Many2one(related='product_id.bailleur_id', string="Bailleur")

    # commision_bailleur = fields.Float(string="Commision bailleur", default=5, related='product_id.commision_bailleur')

    # partner_id = fields.Many2one(related='invoice_id.partner_id')

    # product_id = fields.Many2one('product.product', related='invoice_id.product_id')

    # account_id = fields.Many2one('account.account', string='Compte Agence(Dima)',  related='invoice_id.property_account_income_id')

    type_bien = fields.Selection([
        ('consu', 'bien à vendre'),
        ('service', 'Bien à louer')], string='Product Type', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.', related='product_id.type')


class journal(models.Model):
    _inherit = 'account.journal'


class commission_settlement(models.Model):
    _inherit = "sale.commission.settlement"

    product = fields.Many2one(related='lines.product_id')

    state = fields.Selection(
        selection=[("settled", "A Déverser"),
                   ("invoiced", "Déverser"),
                   ("cancel", "Annulé"),
                   ("except_invoice", "Exception des déversements")], string="State", readonly=True, default="settled")
                   
                     


class SettlementLine(models.Model):
    _inherit = "sale.commission.settlement.line"

    product_id = fields.Many2one(
        comodel_name='product.product', store=True,
        related='agent_line.product_id')


class AccountInvoiceLineAgent(models.Model):
    _inherit = "account.invoice.line.agent"

    product_id = fields.Many2one(
        comodel_name='product.product', store=True,
        related='object_id.product_id')


class SaleCommission(models.Model):
    _name = "sale.commission"
    _description = "Commission in sales"

    name = fields.Char('Nom de la commission', required=True)

    commission_type = fields.Selection(
        selection=[("fixed", "Percentage fixe"),
                   ("section", "Par sections(%)")],
        string="Type", required=True, default="section")
    fix_qty = fields.Float(string="Percentage commission")
    sections = fields.One2many(
        comodel_name="sale.commission.section", inverse_name="commission")
    active = fields.Boolean(default=True)
    invoice_state = fields.Selection(
        [('open', 'Basé sur la facture'),
         ('paid', 'Basé sur la paiement')], string='État de la facture',
        required=True, default='open')
    amount_base_type = fields.Selection(
        selection=[('gross_amount', 'Montant brut'),
                   ('net_amount', 'Montant Net')],
        string='Base', required=True, default='gross_amount')
    settlements = fields.Many2many(
        comodel_name='sale.commission.settlement')

    @api.multi
    def calculate_section(self, base):
        self.ensure_one()
        for section in self.sections:
            if section.amount_from <= base <= section.amount_to:
                return base * section.percent / 100.0
        return 0.0
