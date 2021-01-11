# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json


from odoo import http, SUPERUSER_ID






class Todo(http.Controller):

    @http.route('/hello/boutique', website=True, auth='user')
    def hello(self, **kw):
        product_variant = request.env['product.product'].browse('product_id')
        return request.render("location_biens.hello")

class Main(http.Controller):
    @http.route('/todo', website=True, auth='user')
    def index(self, **kw):
        products = request.env['product.product'].sudo().search([('name_adresse_t', "ilike", self)], order="chambres asc")
        return request.render("location_biens.index", {'product': products})

       
class Main_detail(http.Controller):
    @http.route('/todo/<model("product.product"):task>', website=True)
    def index(self, task, **kw):
        return http.request.render('location_biens.detail',{'product': task})



