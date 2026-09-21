# -*- coding: utf-8 -*-
from odoo import models, fields, _


class MeSalesPaymentMode(models.Model):
    _name = 'me_sales.payment.mode'
    _description = 'Mode de paiement'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    nature = fields.Selection([
        ('cash', 'Espèces'),
        ('cheque', 'Chèque'),
        ('transfer', 'Virement'),
        ('other', 'Autre'),
    ], string='Nature')
    is_default = fields.Boolean(string='Par défaut', default=False)
    active = fields.Boolean(default=True)


class MeSalesPaymentMethod(models.Model):
    _name = 'me_sales.payment.method'
    _description = 'Méthode de paiement'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    is_default = fields.Boolean(string='Par défaut', default=False)
    active = fields.Boolean(default=True)


class MeSalesSaleCondition(models.Model):
    _name = 'me_sales.sale.condition'
    _description = 'Condition de vente'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    is_default = fields.Boolean(string='Par défaut', default=False)
    active = fields.Boolean(default=True)


class MeSalesOfferValidity(models.Model):
    _name = 'me_sales.offer.validity'
    _description = "Durée de validité de l'offre"
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True, translate=True)
    sequence = fields.Integer(required=True, default=10)
    days = fields.Integer(string='Jours', help='Nombre de jours de validité')
    is_default = fields.Boolean(string='Par défaut', default=False)
    active = fields.Boolean(default=True)
