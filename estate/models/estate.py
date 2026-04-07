# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class Estate(models.Model):
    _name = "estate.property"
    _description = "This is a module for estate property management"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price should be strictly above 0'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price should be at least 0'),
    ]
    _order = "id desc"

    # Tuto parties 5 et 6
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.add(fields.Date.context_today(self), months=3)
    )    
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'), 
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
            ]
    )
    active = fields.Boolean(default=True)
    status = fields.Selection(
        copy=False,
        selection=[
            ('new', 'New'),
            ('offer received', 'Offer Received'),
            ('offer accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        default='new',
        required=True
    )

    # Tuto partie 7
    property_type_id = fields.Many2one('estate.property.type', 
                                       string='Property Type')

    buyer_id = fields.Many2one('res.partner', 
                               string='Buyer', 
                               copy=False)
    
    seller_id = fields.Many2one('res.users', 
                                string='Salesman', 
                                default=lambda self: self.env.user)
    
    property_tag_id = fields.Many2many('estate.property.tag', 
                                       string="Tags")

    offer_ids = fields.One2many('estate.property.offer', 
                               'property_id', 
                               string="Offers")
    
    # Tuto partie 8
    total_area = fields.Float(compute='_compute_area_total',
                               readonly=True)

    @api.depends('living_area', 'garden_area')
    def _compute_area_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    best_offer = fields.Float(compute='_compute_best_offer',
                               readonly=True)
    
    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped("price") or [0.0])

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden is True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # Tuto partie 9
    def action_sold(self):
        for property in self:
            if property.status == 'cancelled':
                raise UserError(_("Cancelled properties cannot be sold."))
            property.status = 'sold'
        return True

    def action_cancel(self):
        for property in self:
            if property.status == 'sold':
                raise UserError(_("Sold properties cannot be cancelled"))
            property.status = 'cancelled'
        return True

    # Tuto partie 10
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_and_expected_price(self):
        for property in self:
            if float_is_zero(property.selling_price, precision_digits=2):
                continue
            if float_compare(property.selling_price, 0.9*property.expected_price, precision_digits=2) < 0:
                raise ValidationError("The selling price must be at least 90% of the expected price.")
            
    # Tuto partie 12
    @api.ondelete(at_uninstall=False)
    def _unlink_property(self):
        for record in self:
            if record.status not in ('new', 'cancelled'):
                raise UserError(_('Deleting this property is not allowed.'))

