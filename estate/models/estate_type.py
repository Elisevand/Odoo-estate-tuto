# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class EstateType(models.Model):
    _name = "estate.property.type"
    _description = "This model is used to add info about property type"
    _sql_constraints = [("unique_type", "UNIQUE(name)", "A property type with the same name already exists."),]
    _order = "sequence, name asc"

    name = fields.Char(required=True)
    sequence = fields.Integer()
    offer_count = fields.Integer(compute="_compute_offer_count", store=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id')

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = 0
            for offer in record.offer_ids:
                record.offer_count += 1
