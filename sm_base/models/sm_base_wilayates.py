from odoo import  api, fields, models


class SMBaseWilayates(models.Model):
    """Divisions administratives algériennes (wilayas)."""

    _name = "sm_base.wilayates"
    _description = "Wilayas d'Algérie"
    _order = "sequence, code"

   
    _check_name_code_unique = models.Constraint(
        'UNIQUE(code, name)',
        'Une wilaya avec le même code et le même nom existe déjà !',
    )

    name = fields.Char(
        string="Nom",
        required=True,
        translate=True,
        index=True,
    )
    code = fields.Char(
        string="Code",
        required=True,
        size=2,
        index=True,
    )
    sequence = fields.Integer(
        string="Séquence",
        default=10,
        index=True,
    )
    active = fields.Boolean(
        string="Actif",
        default=True,
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}"
