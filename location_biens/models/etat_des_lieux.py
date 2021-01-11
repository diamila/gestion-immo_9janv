# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from datetime import datetime
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp


class Etat_des_lieux(models.Model):
    _name = 'lb.etat_des_lieux'
    _rec_name = 'bien_loue'

    # kanban
    color = fields.Integer()

    etat_des_lieux_type = fields.Selection(
        [('entree', 'Etat des lieux d\'entrée'), ('pendant', 'Etat des lieux durant la location'),
         ('sortie', 'Etat des lieux de sortie')], string="Type", required=True)
    date_etat_des_lieux = fields.Date(string="Date etat lieu")

    location = fields.Many2one('lb.location', ondelete='cascade', string="Contrat associé", required=True,
                               domain="[('state','=','confirm')]")

    locataires = fields.Many2one(related='location.locataires', string="Locataire")
    mobile = fields.Char(string="N° Tel Locataire", related='location.mobile')

    bien_loue = fields.Many2one(related='location.bien_loue', string="Bien Loué")
    categ_id = fields.Many2one(related='location.categ_id', string="Type Bien")
    adresse = fields.Many2one(related='location.adresse', string="Quartier de visite : ")

    notes = fields.Text(string="Notes")
    user_id = fields.Many2one('res.users', string='Agent-Guide', track_visibility='onchange',
                              default=lambda self: self.env.user)

    enregistrement_etat_des_lieux = fields.One2many('lb.enregistrement_etat_des_lieux', 'etat_des_lieux_id',
                                                    string="Etat des lieux")
    Etat = fields.Selection(
        [('non vérifié.', 'Non vérifié'), ('neuf', 'Neuf'), ('bon etat', 'Bon état'), ('etat moyen', 'Etat moyen'),
         ('mauvais etat', 'Mauvais état')], string="Etat lieu", related='enregistrement_etat_des_lieux.Etat')

    etat_des_lieux_entree_associe = fields.Many2one('lb.etat_des_lieux', ondelete='cascade', string="Location associée")

    # etat_des_lieux_entree_associe = fields.Many2one('lb.etat_des_lieux', string="Etat des lieux d'entrée associé",
    # domain=[('etat_des_lieux_type', '=', 'entree')])
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Documents")

    # 2 fonctions pour l'image attaché

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for etat in self:
            etat.doc_count = Attachment.search_count(
                [('res_model', '=', 'lb.etat_des_lieux'), ('res_id', '=', etat.id)])

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'lb.etat_des_lieux'), ('res_id', 'in', self.ids)]
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

    pendant_etat_des_lieux = fields.One2many('lb.pendant_etat_des_lieux', 'etat_pendant_id',
                                             string="Etat pandant location", required=True)

    Etat_pendant = fields.Selection(
        [('bon etat', 'Bon état'), ('etat moyen', 'Etat moyen'),
         ('mauvais etat', 'Mauvais état')], string="Etat Visite", related='pendant_etat_des_lieux.Etat_pendant')

    date_pendant = fields.Date(string='Date Visite', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                               related='pendant_etat_des_lieux.date_pendant')


class Enregistrement_Etat_des_lieux(models.Model):
    _name = 'lb.enregistrement_etat_des_lieux'

    etat_des_lieux_id = fields.Many2one('lb.etat_des_lieux', ondelete='cascade', string="Etat des lieux")
    nom_piece = fields.Char(string="Nom de la pièce", required=True)
    Etat = fields.Selection(
        [('non vérifié.', 'Non vérifié'), ('neuf', 'Neuf'), ('bon etat', 'Bon état'), ('etat moyen', 'Etat moyen'),
         ('mauvais etat', 'Mauvais état')], string="Etat lieu")
    commentaires = fields.Text(string="Commentaire")

    photos = fields.Binary(string="photos", attachment=True)
    fichier = fields.Binary(string="fichier", attachment=True)


class Enregistrement_Etat_des_lieux_pendant(models.Model):
    _name = 'lb.pendant_etat_des_lieux'

    etat_pendant_id = fields.Many2one('lb.etat_des_lieux', ondelete='cascade', string="Etat des lieux Pandant")
    nom_piece_pendant = fields.Char(string="Résumé", required=True)
    Etat_pendant = fields.Selection(
        [('bon etat', 'Bon état'), ('etat moyen', 'Etat moyen'),
         ('mauvais etat', 'Mauvais état')], string="Etat Visite")
    commentaires_pendant = fields.Text(string="Commentaire")

    date_pendant = fields.Date(string='Date Visite', default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    fichier = fields.Binary(string="fichier", attachment=True)

    photos = fields.Many2many("lb.photos_pendant", string="Photos")


class photos(models.Model):
    _name = 'lb.photos_pendant'
    _rec_name = 'description'

    photos = fields.Binary(string="Photos", attachment=True)
    description = fields.Char('Nom de la pièce')






