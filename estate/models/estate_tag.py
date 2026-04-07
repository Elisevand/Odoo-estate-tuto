# -*- coding: utf-8 -*-

from odoo import models, fields

class Estate_tag(models.Model):
    _name = "estate.property.tag"
    _description = "This model is used to add tags about properties"
    _sql_constraints = [("unique_tag", "UNIQUE(name)", "A tag with the same name already exists."),
                        ]
    _order = "name asc"

    name = fields.Char(required=True)

    # Tuto partie 11
    color = fields.Integer()