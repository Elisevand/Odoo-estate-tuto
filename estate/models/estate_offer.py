# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EstateOffer(models.Model):
    _name = "estate.property.offer"
    _description = "This model is used to keep track of offers"
    _sql_constraints = [('check_price', 'CHECK(price > 0)', 'An offer price should be strictly above 0')]
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ],
        copy=False
    )
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True
    )
    property_id = fields.Many2one(
        'estate.property',
        required=True
    )
    property_type_id = fields.Many2one(
        'estate.property.type',
        related="property_id.property_type_id", 
        store=True
    )
    
    @api.depends('validity', 'create_date')
    def _compute_date_deadline(self):
        for offer in self:
            creation_datetime = offer.create_date or fields.Datetime.now()
            creation_date = fields.Date.to_date(creation_datetime)
            offer.date_deadline = fields.Date.add(creation_date, days=offer.validity or 0)

    def _inverse_date_deadline(self):
        for offer in self:
            creation_datetime = offer.create_date or fields.Datetime.now()
            creation_date = fields.Date.to_date(creation_datetime)
            if offer.date_deadline:
                time_difference = offer.date_deadline - creation_date
                offer.validity = time_difference.days
            else:
                offer.validity = 0

    def action_accept_offer(self):
        for offer in self:
            for other_offer in offer.property_id.offer_ids:
                if other_offer.status == 'accepted' and other_offer.id != offer.id:
                    raise UserError(_("Another offer is already accepted for this property"))
            offer.status = 'accepted'
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.status = 'offer accepted'
        return True

    def action_refuse_offer(self):
        for offer in self:
            offer.status = 'refused'
        return True

    @api.model
    def create(self, vals):
        """Override to ensure a new offer is not lower than existing offers 
        and update property status.
        """
        property_rec = self.env['estate.property'].browse(vals.get('property_id'))
        if property_rec:
            offers = property_rec.offer_ids.mapped('price')
            max_price = max(offers or [0.0])
            if vals.get('price', 0.0) < max_price:
                raise UserError(_("New offer cannot be lower than any offer"))
            if property_rec.status == 'new':
                property_rec.status = 'offer received'
        return super().create(vals)
