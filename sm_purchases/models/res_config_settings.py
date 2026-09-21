# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # Paramètres des produits
    can_change_product_designation_on_purchases = fields.Boolean(
        string='Peut modifier la désignation du produit lors des achats',
        config_parameter='sm_purchases.can_change_product_designation_on_purchases',
        default=False,
    )


    # # Paramètres d'affichage
    # show__line_numbers = fields.Boolean(
    #     string='Afficher les numéros de ligne',
    #     config_parameter='sm_purchases.show_line_numbers',
    #     default=False,
    # )
    # show_product_code = fields.Boolean(
    #     string='Afficher le code produit fournisseur',
    #     config_parameter='sm_purchases.show_product_code',
    #     default=False,
    # )
    # editable_product_name = fields.Boolean(
    #     string='Nom du produit modifiable',
    #     config_parameter='sm_purchases.editable_product_name',
    #     default=False,
    # )

    # # Paramètres de remise
    # discount_enabled = fields.Boolean(
    #     string='Activer les remises',
    #     config_parameter='sm_purchases.discount_enabled',
    #     default=False,
    # )
    # discount_method = fields.Selection(
    #     [
    #         ('rate', 'Taux'),
    #         ('amount', 'Montant'),
    #     ],
    #     string='Méthode de remise par défaut',
    #     config_parameter='sm_purchases.discount_method',
    #     default='rate',
    # )

    # discount_rate = fields.Float(
    #     string='Taux de remise par défaut (%)',
    #     config_parameter='sm_purchases.discount_rate',
    #     default=5.0,
    # )
    # discount_amount = fields.Float(
    #     string='Montant de remise par défaut',
    #     config_parameter='sm_purchases.discount_amount',
    #     default=0.0,
    # )

 