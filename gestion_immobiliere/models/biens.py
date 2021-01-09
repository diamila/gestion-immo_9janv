# -*- coding: utf-8 -*-

from lxml import etree

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons import decimal_precision as dp


class BienNormal_desc(models.Model):
    _inherit = 'product.product'

    google_map_partner = fields.Char(string="Map")

    @api.onchange('longitude', 'latitude')
    def get_localisation(self):
        for rec in self:
            rec.google_map_partner = 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d15438.888445307135!2d-' + str(rec.longitude) + '!3d' + str(rec.latitude) + '!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0xec16d63db2a9e4d%3A0x4e3727affd9a03a6!2sTERROU-BI%20RESORT!5e0!3m2!1sfr!2ssn!4v1606731809395!5m2!1sfr!2ssn'

    @api.onchange('superficie', 'name_adresse', 'name_categ_id', '  chambres', 'salons', 'salles_bain', 'cuisines',
                  'toilette', 'parking', 'balcon')
    def get_test(self):
        for rec in self:
            if rec.superficie:
                rec.web_description = str(rec.name_categ_id) + ' est situé à ' + str(
                    rec.name_adresse) + ' superficie : ' + str(
                    rec.superficie)
            else:
                rec.web_description = str(rec.name_categ_id) + ' est situé à ' + str(
                    rec.name_adresse) + '/ Composant : '

    web_description = fields.Char('Description', compute='get_test')


class BienNormal_template_etat(models.Model):
    _inherit = 'product.template'
    
    
    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'MA')], limit=1)
        return country

    pays_site = fields.Many2one('res.country', string="Pays", default=_get_default_country)

    name_pays_site = fields.Char(string="Nom Quartier", related='pays_site.name')
    
    name = fields.Char('Name', index=True, required=True, translate=True)
    
    superficie_site = fields.Float(String="Superficie(m²)")

    quartier_site = fields.Many2one('lb.quartier', string="Quartier", required=True)

    name_quartier_site = fields.Char(string="Nom Quartier", related='quartier_site.nom_quartier')

    rue_site = fields.Char(string="Rue")

    ville_site = fields.Many2one('lb.ville', string="Ville")
    
    @api.model
    def default_get(self, fields):
        res = super(BienNormal_template_etat, self).default_get(fields)
        print("test......")
        res['ville_site'] = 1
        res['public_categ_ids'] = 35
        return res
    
    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category', required=True,
                                        help="The product will be available in each mentioned e-commerce category. Go to"
                                             "Shop > Customize and enable 'E-commerce categories' to view all e-commerce categories."
                                        )
                                        
    name_categ_id = fields.Char(related='categ_id.name', string="Catégorie du Bien")                               

    parent_id = fields.Many2one('product.public.category', string='Parent Category',
                                related='public_categ_ids.parent_id')

    @api.onchange('parent_id', 'name_categ_id')
    def _onchange_actions(self):
        if self.type == 'service':
            if self.name_categ_id == 'Appartement':
                return {
                    'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Appartement')]}}
            if self.name_categ_id == 'Studio':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Studio')]}}
            if self.name_categ_id == 'Terrain':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Terrain')]}}
            if self.name_categ_id == 'Magasin':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Magasin')]}}
            if self.name_categ_id == 'Villa':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Villa')]}}
            if self.name_categ_id == 'Chambre':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Chambre')]}}
            else:
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer')]}}
        if self.type == 'consu':
            if self.name_categ_id == 'Appartement':
                return {
                    'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Appartement')]}}
            if self.name_categ_id == 'Studio':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Studio')]}}
            if self.name_categ_id == 'Terrain':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Terrain')]}}
            if self.name_categ_id == 'Magasin':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Magasin')]}}
            if self.name_categ_id == 'Villa':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Villa')]}}
            else:
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre')]}}
    

    nom_ville_site = fields.Char(string="Ville", related='ville_site.nom')

    nbre_tour_t = fields.Integer(string="Niveau", related='product_variant_id.nbre_tour')

    nom_ville_t = fields.Char(string="Ville", related='product_variant_id.nom_ville')

    etat_b = fields.Selection([
        ('draft', 'Disponible'),
        ('confirm', 'Bien En location'),
        ('ferme', 'Bien Disponible'),
    ], related='product_variant_id.etat')

    state_vente_t = fields.Selection([
        ('draft', 'ien disponible'),
        ('confirm', 'Bien Vendu'),
    ], related='product_variant_id.state_vente')


class BienNormal_template(models.Model):
    _inherit = 'product.template'

    @api.onchange('name_categ_id_t', 'superficie_t', 'name_adresse_t', 'chambres_t', 'salons_t', 'cuisines_t',
                  'toilette_t')
    def get_test(self):
        for rec in self:
            if rec.superficie_t:
                rec.web_description = rec.name_categ_id_t + ' est situé à ' + rec.name_adresse_t + '/ superficie : ' + str(
                    rec.superficie_t) + 'm2'
            else:
                rec.web_description = str(rec.name_categ_id_t) + ' est situé à ' + str(
                    rec.name_adresse_t) + '/ Caractéristiques : '

    web_description = fields.Char('Website Descriptions',
                                  help="This description", compute='get_test')

    salons_t = fields.Float(string="Nombre salons", related='product_variant_id.salons')

    cuisines_t = fields.Float(string="Nombre cuisines", related='product_variant_id.cuisines')

    toilette_t = fields.Float(string="Nombre toilettes", related='product_variant_id.toilette')

    superficie_t = fields.Float(string="Superficie(m²)", related='product_variant_id.superficie')

    name_categ_id_t = fields.Char(string="Catégorie du Bien", related='product_variant_id.name_categ_id')

    salles_bain_t = fields.Char(string="Nombre salles de bains", related='product_variant_id.salles_bain')

    chambres_t = fields.Float(string="Nombre chambres", related='product_variant_id.chambres')

    adresse_t = fields.Many2one('lb.quartier', string="Quartier", required=True, related='product_variant_id.adresse')

    name_adresse_t = fields.Char(string="Nom Quartier", related='product_variant_id.name_adresse')

    public_categ_ids_t = fields.Many2many('product.public.category', string='Website Product Category', required=True,
                                          help="The product will be available in each mentioned e-commerce category. Go to"
                                               "Shop > Customize and enable 'E-commerce categories' to view all e-commerce categories."
                                          , related='product_variant_id.public_categ_ids')

    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category', required=True,
                                        help="The product will be available in each mentioned e-commerce category. Go to"
                                             "Shop > Customize and enable 'E-commerce categories' to view all e-commerce categories.")

    cour = fields.Float(string="Espace familiale", related='product_variant_id.cour')

    parking = fields.Char(string="Nombre parkings", related='product_variant_id.parking')
    balcon = fields.Char(string="Nombre balcons", related='product_variant_id.balcon')
    jardin = fields.Boolean(default=False, string="Jardin", related='product_variant_id.jardin')
    ascenseur = fields.Boolean(default=False, string="Ascenseur", related='product_variant_id.ascenseur')
    g_electroge = fields.Boolean(default=False, string="Groupe electrogène", related='product_variant_id.g_electroge')

    rue = fields.Char(string="Rue", related='product_variant_id.rue')


class BienNormal(models.Model):
    _inherit = 'product.product'



    @api.model
    def _get_default_country(self):
        country = self.env['res.country'].search([('code', '=', 'MA')], limit=1)
        return country

    ref = fields.Char(string="ref", default="00125")

    # name_a = fields.Char(string="ref", default="aaaaa")

    # name = fields.Char(string="name_n", compute='_fname')

    name_seq = fields.Char(string='seq', required=True, copy=False, readonly=True,
                           index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('bien.sequence') or _('New')
        result = super(BienNormal, self).create(vals)
        return result

    latitude = fields.Char(string="Latitude", default="0.0")
    longitude = fields.Char(string="Longitude", default="0.0")
    Date = fields.Date()
    nbre_tour = fields.Integer(string="Niveau")
    ameublement = fields.Char(string="Ameublement")

    lst_price = fields.Float(related='list_price', readonly=False,
                             digits=dp.get_precision('Product Price'))

    property_account_income_categ_id = fields.Many2one('account.account', company_dependent=True,
                                                       string="Income account", oldname="property_account_income",
                                                       domain=[('deprecated', '=', False)],
                                                       help="Keep this field empty to use the default value from the product category.",
                                                       related='categ_id.property_account_income_categ_id')

    expense_policy = fields.Selection(
        [('no', 'No'), ('cost', 'At cost'), ('sales_price', 'Prix')],
        string='Re-Invoice Policy',
        default='no',
        help="Expenses and vendor bills can be re-invoiced to a customer."
             "With this option, a validated expense can be re-invoice to a customer at its cost or sales price.")

    purchase_ok = fields.Boolean('Can be Purchased', default=False)

    type = fields.Selection([
        ('consu', 'Bien à vendre'),
        ('service', 'Bien à louer')], string='Type de bien', default='consu', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')

    # contrat = fields.Many2one('lb.location', ondelete='cascade', string="Contrat lié au bien")

    location_ok = fields.Boolean(
        'Peut étre en location', default=True)

    type_id = fields.Many2one('lb.type', ondelete='cascade', string="Type bien")
    gestionnaire_id = fields.Many2one('lb.gestionnaire', ondelete='cascade', string="gestionnaire Immeuble", store=True)

    bailleur_id = fields.Many2one('lb.bailleur', string="Bailleur")

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Compte bailleur", oldname="property_account_payable",
                                                  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner",
                                                  related='bailleur_id.property_account_payable_id')

    taux_commission = fields.Float('Taux de commission de l agence SDG(%)', default=0)

    commision_agence = fields.Float(string="Commision agence", default=5, compute='_commissionagence')

    @api.onchange('taux_commission', 'lst_price')
    def _commissionagence(self):
        for r in self:
            r.commision_agence = (r.lst_price * r.taux_commission) / 100

    commision_bailleur = fields.Float(string="Déversement bailleur", default=5, compute='_commissionbailleur')

    @api.onchange('taux_commission', 'lst_price')
    def _commissionbailleur(self):
        for r in self:
            r.commision_bailleur = (r.lst_price * (100 - r.taux_commission)) / 100

    civilite = fields.Selection([('m.', 'M.'), ('mme', 'Mme'), ('mlle', 'Mlle'), ('m. et mme', 'M. et Mme')],
                                string="Civilité", related='bailleur_id.civilite')
    num_piece_identite = fields.Char(string='Numéro de la pièce d\'identité', related='bailleur_id.num_piece_identite')
    street = fields.Char(string="Adresse1", related='bailleur_id.street')
    mobile = fields.Char(string="Mobile", related='bailleur_id.mobile')

    chambres = fields.Float(string="Nombre chambres")
    salons = fields.Float(string="Nombre salons")
    cuisines = fields.Float(string="Nombre cuisines")
    toilette = fields.Float(string="Nombre toilettes")
    cour = fields.Float(string="Espace familiale")

    salles_bain = fields.Char(string="Nombre salles de bains")
    parking = fields.Char(string="Nombre parkings")
    balcon = fields.Char(string="Nombre balcons")
    jardin = fields.Boolean(default=False, string="Jardin")
    ascenseur = fields.Boolean(default=False, string="Ascenseur")
    g_electroge = fields.Boolean(default=False, string="Groupe electrogène")

    oriente_vers = fields.Char(string="Position", default='Bordure route principale')
    # compte_revenu = fields.Many2one('lb.revenu', ondelete='cascade', string="Compte de Revenu")
    # compte_depense = fields.Many2one('ldu Bien")

    name_adresse = fields.Char(string="Nom Quartier", compute='_fon_name_adresse')

    @api.onchange('name_quartier_site')
    def _fon_name_adresse(self):
        for r in self:
            r.name_adresse = r.name_quartier_site

    adresse = fields.Many2one('lb.quartier', string="Quartier", compute='_fon_adresse')

    @api.onchange('quartier_site')
    def _fon_adresse(self):
        for r in self:
            r.adresse = r.quartier_site

    rue = fields.Char(string="Rue", compute='_fon_rue')

    @api.onchange('rue_site')
    def _fon_rue(self):
        for r in self:
            r.rue = r.rue_site

    ville = fields.Many2one('lb.ville', string="Ville", compute='_fon_ville')

    @api.onchange('ville_site')
    def _fon_ville(self):
        for r in self:
            r.ville = r.ville_site

    nom_ville = fields.Char(string="Ville", compute='_fon_nom_ville')

    @api.onchange('nom_ville_site')
    def _fon_nom_ville(self):
        for r in self:
            r.nom_ville = r.nom_ville_site

    pays = fields.Many2one('res.country', string="Pays", dcompute='_fon_pays')

    
    @api.onchange('pays_site')
    def _fon_pays(self):
        for r in self:
            r.pays = r.pays_site

    notes = fields.Text(string="Notes")

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('lb.location'),
                                 index=1)
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')

    # 2 fonctions pour l'image attaché
    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for bien in self:
            bien.doc_count = Attachment.search_count([('res_model', '=', 'lb.bien'), ('res_id', '=', bien.id)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.bien'), ('res_id', 'in', self.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                            Cliquez sur créer (et non importer) pour ajouter les images associées à vos biens.</p><p>
                        </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    # Calcul de la devise
    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    # kanban: qui affiche les sessions regroupées par cours (les colonnes sont donc des cours)
    color = fields.Integer()

    # géolocalisation du bien
    def tt_locate_bien(self):
        return {
            "type": "ir.actions.act_url",
            "url": 'https://www.google.com/maps/search/?api=1&query=' + self.longitude + ', -' + self.latitude,
        }

    # champs: lien avec les information du bien
    history_ids = fields.Many2many('lb.history', string="History")
    plus_proche_ids = fields.Many2many('lb.lieu', string="Lieux plus proche")
    sous_propriete_ids = fields.Many2many('lb.sous_propriete', string="Détail des pièces")

    # champs: Plans d'étage, photos et documents
    plan_ids = fields.Many2many('lb.plan_etage', string="Plans")
    photos_ids = fields.Many2many('lb.photos', string="Photos")
    documents_ids = fields.Many2many('lb.documents', string="Documents")

    # @api.multi
    # def get_name(self):
    # for rec in self:
    # res.append((rec.nom, '%s - %s' % (prix_location)))
    # return res

    contrat_count = fields.Integer(string='Contrats', compute='get_contrat_count')

    @api.multi
    def open_bien_contrat(self):
        return {
            'name': _('Contrats'),
            'domain': [('bien_loue', '=', self.id)],
            'view_type': 'form',
            'res_model': 'lb.location',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_contrat_count(self):
        count = self.env['lb.location'].search_count([('bien_loue', '=', self.id)])
        self.contrat_count = count

    contrat_count_vente = fields.Integer(string='Contrats de vente', compute='get_contrat_count_vente')

    @api.multi
    def open_bien_contrat_vente(self):
        return {
            'name': _('Contrats'),
            'domain': [('bien_loue', '=', self.id)],
            'view_type': 'form',
            'res_model': 'lb.contrat_vente',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_contrat_count_vente(self):
        count = self.env['lb.contrat_vente'].search_count([('bien_loue', '=', self.id)])
        self.contrat_count_vente = count

    # états/barre LOCATION
    state_vente = fields.Selection([
        ('draft', 'ien disponible'),
        ('confirm', 'Bien Vendu'),
    ], compute='_onchangeEtat_vente')

    @api.onchange('bien_loue')
    def _onchangeEtat_vente(self):
        for r in self:
            # récuperer la dernier valeur du modele location et  (state)
            appointments = self.env['lb.contrat_vente'].search([('bien_loue', '=', r.id)])
            if appointments:
                for rec in appointments:
                    r.state_vente = rec.state

    # state = fields.Selection([
    # ('draft', 'New'),
    # ('confirm', 'En location'),
    # ('ferme', 'Fermé'),
    #  ], string='Status', related='etat.state')

    # open maintenance
    maintenance_count = fields.Integer(string='Maintenances', compute='get_maintenance_count')

    @api.multi
    def open_bien_maintenance(self):
        return {
            'name': _('Maintenance'),
            'domain': [('bien_loue', '=', self.id)],
            'view_type': 'form',
            'res_model': 'maintenance.request',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_maintenance_count(self):
        count = self.env['maintenance.request'].search_count([('bien_loue', '=', self.id)])
        self.maintenance_count = count

    # etat = fields.Char(compute='_onchangeEtat')

    etat_n = fields.Selection([
        ('draft', 'Bien Disponible'),
        ('confirm', 'Bien En location'),
        ('ferme', 'Bien Disponible'),
    ], compute='_onchangeetat_n')

    @api.onchange('etat')
    def _onchangeetat_n(self):
        for r in self:
            r.etat_n = r.etat

    etat = fields.Selection([
        ('draft', 'Bien Disponible'),
        ('confirm', 'Bien En location'),
        ('ferme', 'Bien Disponible'),
    ], compute='_onchangeEtat')

    @api.onchange('bien_loue')
    def _onchangeEtat(self):
        for r in self:
            # récuperer la dernier valeur du modele location et  (state)
            appointments = self.env['lb.location'].search([('bien_loue', '=', r.id)], order='id desc', limit=1)
            if appointments:
                for rec in appointments:
                    r.etat = rec.state
            else:
                r.etat = 'ferme'

    @api.multi
    def print_report(self):
        return self.env.ref('gestion_immobiliere.contrat_bailleur').report_action(self)

    name_categ_id = fields.Char(related='categ_id.name', string="Catégorie du Bien")
    

    superficie = fields.Float(String="Superficie(m²)",compute='_fon_superficie')
    

    @api.onchange('superficie_site')
    def _fon_superficie(self):
        for r in self:
            r.superficie = r.superficie_site


class BienNormal_template_product(models.Model):
    _name = "lb.product_t"
    _inherit = ['product.template', 'product.product']

    default_code = fields.Char()

    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category', required=True,
                                        help="The product will be available in each mentioned e-commerce category. Go to"
                                             "Shop > Customize and enable 'E-commerce categories' to view all e-commerce categories."
                                        )
                                        
                                   

    parent_id = fields.Many2one('product.public.category', string='Parent Category',
                                related='public_categ_ids.parent_id')

    @api.onchange('parent_id', 'name_categ_id')
    def _onchange_action(self):
        if self.type == 'service':
            if self.name_categ_id == 'Appartement':
                return {
                    'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Appartement')]}}
            if self.name_categ_id == 'Studio':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Studio')]}}
            if self.name_categ_id == 'Terrain':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Terrain')]}}
            if self.name_categ_id == 'Magasin':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Magasin')]}}
            if self.name_categ_id == 'Villa':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Villa')]}}
            if self.name_categ_id == 'Chambre':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer'), ('name', '=', 'Chambre')]}}
            else:
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à louer')]}}
        if self.type == 'consu':
            if self.name_categ_id == 'Appartement':
                return {
                    'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Appartement')]}}
            if self.name_categ_id == 'Studio':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Studio')]}}
            if self.name_categ_id == 'Terrain':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Terrain')]}}
            if self.name_categ_id == 'Magasin':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Magasin')]}}
            if self.name_categ_id == 'Villa':
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre'), ('name', '=', 'Villa')]}}
            else:
                return {'domain': {'public_categ_ids': [('parent_id', '=', 'Bien à vendre')]}}


class Type(models.Model):
    _name = 'lb.type'
    _rec_name = 'type'

    type = fields.Char(string="Type")


class gestionnaire(models.Model):
    _name = 'lb.gestionnaire'
    _rec_name = 'gestionnaire_immeuble'

    gestionnaire_immeuble = fields.Char(string="Nom gestionnaire immeuble")


# -------------------informations
class history(models.Model):
    _name = 'lb.history'
    _rec_name = 'source'

    date = fields.Date('Date')
    source = fields.Char('Source')
    number = fields.Char('Number')


class type_lieu(models.Model):
    _name = 'lb.type_lieu'
    _rec_name = 'type_lieu'

    type_lieu = fields.Char('Type de lieu')


class plus_proche(models.Model):
    _name = 'lb.lieu'
    _rec_name = 'name_lieu'

    name_lieu = fields.Char('Nom du lieu')
    type_lieu = fields.Many2one('lb.type_lieu', string="Type de lieu")
    distance = fields.Float(string="Distance(m)", default=5)


class sous_propriete(models.Model):
    _name = 'lb.sous_propriete'
    _rec_name = 'type_piece'

    type_piece = fields.Many2one('lb.type_piece', string="Type de pièces")
    height = fields.Float(string="longueur(m)", default=3.0)
    width = fields.Float(string="Largeur(m)", default=2.0)


class type_piece(models.Model):
    _name = 'lb.type_piece'
    _rec_name = 'type_piece'

    type_piece = fields.Char('Type de pièces')


class Plans_etage(models.Model):
    _name = 'lb.plan_etage'
    _rec_name = 'description_plan'

    description_plan = fields.Char('Description plan')
    photos_plan = fields.Binary(string="Photos plan", attachment=True)


class photos(models.Model):
    _name = 'lb.photos'
    _rec_name = 'description'

    description = fields.Char('Description')
    photos = fields.Binary(string="Photos", attachment=True)


class documents(models.Model):
    _name = 'lb.documents'
    _rec_name = 'description'

    description = fields.Char('Description')
    date_expiration = fields.Date('Date expiration')
    fichier = fields.Binary(string="Fichiers", attachment=True)


class Maintenance(models.Model):
    _inherit = 'maintenance.request'

    cout_maintenance = fields.Float(string="coût maintenance", default=0.0)
    bien_loue = fields.Many2one('product.product', required=True, String="Bien")


class CRM(models.Model):
    _inherit = 'crm.lead'

    type_propect = fields.Selection(
        [('location', 'Location'), ('gerance', 'Gérance'), ('location', 'Location + Gérance')],
        String="Type de Prospect")

    besoin = fields.Selection(
        [('location', 'Location'), ('ach', 'Achat')],
        string="Type Besoin", related='partner_id.besoin')

    # info = fields.Char(default="veiller enregistre les modification pr que Ce prospect soit un locataire")

    active_potenctiels = fields.Selection(
        [('client', 'est un Client'), ('prospect', 'Est Un Prospect')],
        string="Statut contact", related='partner_id.active_potenctiel', default='prospect',  compute='_onchange_stage_i')
        
    #name_stage = fields.Char(related="stage_id.name")    
    
    @api.onchange('probability')
    def _onchange_active_potenctielst(self):
        if self.probability == 0:
            for task in self:
                task.partner_id.active = not task.partner_id.active
                return self.write(
                    {'active': False, 'task.partner_id.active': False})
            
    # test = fields.Boolean(compute='create_locataire')

    client_type = fields.Selection(
        [('client_ache', 'Client Acheteur'), ('client_loc', 'Client Locataire')],
        string="Statut client", related='partner_id.client_type', default='client_loc')

    @api.onchange('probability')
    def _onchange_stage_i(self):
        if self.probability == 0:
            self.active = False
            return True

    active_test = fields.Boolean(related='partner_id.active')

    @api.multi
    def action_set_lost(self):
        """ Lost semantic: probability = 0, active = False """
        for task in self:
            task.partner_id.active = not task.partner_id.active
            task.probability = 0
            return self.write(
                {'probability': 0, 'active': False, 'active_test': False, 'task.partner_id.active': False})

    @api.multi
    def action_set_won(self):
        """ Won semantic: probability = 100 (active untouched) """
        for lead in self:
            stage_id = lead._stage_find(domain=[('probability', '=', 100.0), ('on_change', '=', True)])
            lead.write({'stage_id': stage_id.id, 'probability': 100})
            if (self.partner_id.active_potenctiel) == 'prospect':
                if (self.besoin) == 'location':
                    self.partner_id.client_type = 'client_loc'
                    self.partner_id.active_potenctiel = 'client'
                    return True
                if (self.besoin) == 'ach':
                    self.partner_id.client_type = 'client_ache'
                    self.partner_id.active_potenctiel = 'client'
                    return True
            else:
                self.partner_id.active_potenctiel = 'client'

    @api.one
    def terminer_basculer(self):
        if (self.partner_id.active_potenctiel) == 'prospect':
            self.partner_id.active_potenctiel = 'client'
            self.partner_id.client_type = 'client_loc'
            return True
        else:
            self.partner_id.active_potenctiel = 'client'
            self.partner_id.client_type = 'client_loc'

    @api.one
    def terminer_basculer_acheteur(self):
        if (self.partner_id.active_potenctiel) == 'prospect':
            self.partner_id.active_potenctiel = 'client'
            self.partner_id.client_type = 'client_ache'
            return True
        else:
            self.partner_id.active_potenctiel = 'client'
            self.partner_id.client_type = 'client_ache'

    def locataires(self):
        return {
            'name': _('Locataire'),
            'domain': [('client_type', '=', 'client_loc'), ('active_potenctiel', '=', 'client'),
                       ('customer', '=', True), ('parent_id', '=', False)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }

    def acheteurs(self):
        return {
            'name': _('Acheteur'),
            'domain': [('client_type', '!=', 'client_loc'), ('active_potenctiel', '=', 'client'),
                       ('customer', '=', True), ('parent_id', '=', False)],
            'view_type': 'form',
            'res_model': 'res.partner',
            'view_id': False,
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
        }

class CRM_suite(models.Model):
    _inherit = 'crm.lead'

    type_besoin = fields.Text(related='partner_id.type_besoin', string="Besoin du prospect", required=True)

  
    
    planned_revenue = fields.Float(related='partner_id.planned_revenue', string="Budget", default=0.0, compute='_onchangebudget', required=True)
        


class CRM_quartier_souhaitee(models.Model):
    _inherit = 'crm.lead'

    quartier_souhaitee = fields.Many2many('lb.quartier', related='partner_id.quartier_souhaitee', string="Quartiers souhaités", required=True)


class CRM_locatire(models.Model):
    _inherit = 'crm.lead'

    locatiare_crm_id = fields.Many2one('res.partner')


class CRM_onchage(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('partner_id.active_potenctiel')
    def _check_etat_bien(self):
        for r in self:
            if (r.partner_id.active_potenctiel) == 'prospect':
                return {
                    'warning': {
                        'title': "Ce bien est en location",
                    },
                }

