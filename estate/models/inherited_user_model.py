

from odoo import fields, models

class Property_inherited_users(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'seller_id', 
                                   domain=[('status', 'not in', ['sold', 'cancelled'])])
    