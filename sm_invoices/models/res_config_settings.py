# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ------------------------------------------------------------------
    # Paramètres des produits
    # ------------------------------------------------------------------
    can_change_product_designation_on_invoices = fields.Boolean(
        string="Peut modifier la désignation du produit lors des factures",
        config_parameter='sm_invoices.can_change_product_designation_on_invoices',
        default=False,
        help="Permet de modifier la désignation du produit sur les lignes de facture.",
    )

    # ------------------------------------------------------------------
    # Paramètres de TVA (factures uniquement)
    # ------------------------------------------------------------------
    tva_enabled = fields.Boolean(
        string="Activer la TVA sur les factures",
        config_parameter='sm_invoices.tva_enabled',
        default=False,
        help="Activer le calcul de la TVA sur les factures clients.",
    )
    tva_taux = fields.Float(
        string="Taux de TVA par défaut (%)",
        config_parameter='sm_invoices.tva_taux',
        default=19.0,
        help="Taux de TVA par défaut appliqué aux nouvelles factures.",
    )

    # ------------------------------------------------------------------
    # Paramètres de remise (factures uniquement)
    # ------------------------------------------------------------------
    remise_exist = fields.Boolean(
        string="Activer les remises sur les factures",
        config_parameter='sm_invoices.remise_exist',
        default=False,
        help="Activer les champs de remise sur les factures clients.",
    )
    remise_methode = fields.Selection(
        [
            ('taux', 'Taux'),
            ('mta', 'Montant'),
        ],
        string="Méthode de remise par défaut",
        config_parameter='sm_invoices.remise_methode',
        default='taux',
        help="Choisir la méthode de remise par défaut pour les nouvelles factures.",
    )
    remise_default_taux = fields.Float(
        string="Taux de remise par défaut (%)",
        config_parameter='sm_invoices.remise_default_taux',
        default=5.0,
        help="Taux de remise par défaut appliqué aux nouvelles factures.",
    )
    remise_default_mta = fields.Float(
        string="Montant de remise par défaut",
        config_parameter='sm_invoices.remise_default_mta',
        default=0.0,
        help="Montant fixe de remise par défaut.",
    )
