# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Estate_type(models.Model):
    _name = "estate.property.type"
    _description = "This model is used to add info about property type"
    _sql_constraints = [("unique_type", "UNIQUE(name)", "A property type with the same name already exists."),
                        ]
    _order = "sequence, name asc"

    name = fields.Char(required=True)

    # Tuto partie 11
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer()
    
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
    offer_count = fields.Integer(compute="_compute_offer_count", store=True)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = 0
            for offer in record.offer_ids:
                record.offer_count += 1
