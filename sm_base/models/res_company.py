from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # ── Localisation ──────────────────────────────────────────────────
    wilaya_id = fields.Many2one(
        comodel_name="sm_base.wilayates",
        string="Wilaya",
        ondelete="set null",
    )

    # ── Coordonnées ───────────────────────────────────────────────────
    mobile = fields.Char(string="Téléphone mobile")
    fax = fields.Char(string="Fax")
    boite_postale = fields.Char(string="B.P.", help="Boîte postale")

    # ── Identifiants fiscaux et commerciaux algériens ────────────────
    nis = fields.Char(
        string="NIS",
        help="Numéro d'Identification Statistique",
    )
    rib = fields.Char(
        string="RIB",
        help="Relevé d'Identité Bancaire",
    )
    capital_social = fields.Char(string="Capital Social")
    m_fisc = fields.Char(
        string="Mat. Fisc.",
        help="Matricule Fiscal",
    )
    a_imp = fields.Char(
        string="Art. Imp.",
        help="Article d'Imposition",
    )
    reg_com = fields.Char(
        string="Reg. Com.",
        help="Registre du Commerce",
    )
    slogon=fields.Char("Slogon")
