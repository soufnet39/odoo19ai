# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Paramètres généraux
    confirm_orders_by_default = fields.Boolean(
        string='Confirmer les commandes par défaut',
        config_parameter='sm_sales.confirm_orders_by_default',
        default=False,
    )
    # Paramètres généraux
    confirm_purchase_by_default = fields.Boolean(
        string='Confirmer les achats par défaut',
        config_parameter='sm_sales.confirm_purchase_by_default',
        default=False,
    )
    # Paramètres des produits
    can_change_product_designation_on_sales = fields.Boolean(
        string='Peut modifier la désignation du produit lors des ventes',
        config_parameter='sm_sales.can_change_product_designation_on_sales',
        default=False,
    )

    # Paramètres d'affichage
    show_line_numbers = fields.Boolean(
        string='Afficher les numéros de ligne',
        config_parameter='sm_sales.show_line_numbers',
        default=False,
    )
    show_product_code = fields.Boolean(
        string='Afficher le code produit',
        config_parameter='sm_sales.show_product_code',
        default=False,
    )
    editable_product_name = fields.Boolean(
        string='Nom du produit modifiable',
        config_parameter='sm_sales.product_name_editable',
        default=False,
    )

    # Paramètres de TVA (pour les commandes et les achats) -------
    tva_enabled = fields.Boolean(
        string='Activer la TVA',
        config_parameter='sm_sales.tva_enabled',
        default=False,
    )
    tva_taux = fields.Float(
        string='Taux de TVA par défaut (%)',
        config_parameter='sm_sales.tva_taux',
        default=19.0,
    )
    # -----------------------------------------------------

    # Paramètres de remise (pour les commandes et les achats) ----
    discount_enabled = fields.Boolean(
        string='Activer les remises',
        config_parameter='sm_sales.remise_exist',
        default=False,
    )
    discount_method = fields.Selection(
        [
            ('taux', 'Taux'),
            ('amount', 'Montant'),
        ],
        string='Méthode de remise par défaut',
        config_parameter='sm_sales.remise_methode',
        default='taux',
    )    
    discount_taux = fields.Float(
        string='Taux de remise par défaut (%)',
        config_parameter='sm_sales.remise_default_taux',
        default=5.0,
    )
    discount_amount = fields.Float(
        string='Montant de remise par défaut',
        config_parameter='sm_sales.remise_default_mta',
        default=0.0,
    )
    # -----------------------------------------------------

 