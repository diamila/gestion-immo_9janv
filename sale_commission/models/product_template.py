
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    commission_free = fields.Boolean(string="Sans commission",
                                     default=False)
