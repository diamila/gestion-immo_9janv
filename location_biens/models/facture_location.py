from odoo import models, fields, api, tools, exceptions, _
from datetime import datetime, timedelta

import re
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp

from odoo.exceptions import ValidationError


# FACTURATION
class Paiement_location(models.Model):
    _name = 'lb.paiement_location'
    _rec_name = 'product_id'
    
    

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        form_view = [(self.env.ref('account.invoice_form').id, 'form')]
        return action

    contrat = fields.Many2one('lb.location', string="Contrat associé", domain="[('state','=','confirm')]",
                              required=True)

    invoice_count = fields.Integer(string='Invoice Count', compute='_get_invoiced')

    def _get_invoiced(self):
        count = self.env['account.invoice'].search_count([('contrat_t', '=', self.id)])
        self.invoice_count = count

    @api.multi
    def action_facture(self):

        return {
            'name': _('account.invoice'),
            'domain': [('contrat_t', '=', self.id)],
            'view_type': 'form',
            'view_id': False,
            'views': [(self.env.ref('account.invoice_kanban').id, 'kanban'),(self.env.ref('account.invoice_tree').id, 'tree'), (self.env.ref('account.invoice_form').id, 'form')],
            'res_model': 'account.invoice',
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def print_facture(self):
        return self.env.ref('location_biens.facture_card_location').report_action(self)

    date_paiement = fields.Date(string='Date', required=True,
                                default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # kanban
    color = fields.Integer()

    ref_facture = fields.Char(string="Identifiant", help="Identifiant unique de facturation")

    product_id = fields.Many2one(related='contrat.bien_loue', string="Bien")

    # bien_loue = fields.Many2one(related='invoice_line_ids.bien_loue', string="bien")

    locataire_id = fields.Many2one(related='contrat.locataires', string="Locataire", store=True)

    partner_id = fields.Many2one(related='contrat.locataires', string="Locataire", store=True)

    mobile = fields.Char(string="N° Tel Locataire", related='contrat.mobile')

    # états/barre LOCATION
    state = fields.Selection([
        ('draft', 'New Contrat'),
        ('confirm', 'Contrat en cour'),
        ('ferme', 'Contrat Achevé'),
    ], string='Status', related='contrat.state')

    categ_id = fields.Many2one(related='contrat.categ_id', string="Catégorie du bien")

    type = fields.Selection([
        ('consu', 'bien à vendre'),
        ('service', 'Bien à loué')], string='Type de bien', default='service', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.', related='contrat.type')

    price_unit = fields.Float(related='contrat.loyer_sans_charges', string="Prix loyer/mois")

    montant_location = fields.Float(related='contrat.loyer_sans_charges', string="Prix loyer/mois")

    commentaire_paiement = fields.Text(string="Commentaire")

















