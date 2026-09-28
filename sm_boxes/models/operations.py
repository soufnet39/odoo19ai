from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class BoxesOperationsModule(models.Model):
    _name = 'sm_boxes.operations'
    _description = 'Opération de caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    operation = fields.Selection(string="Opération", selection=[
                                ('recette', 'Recette'),
                                ('depence', 'Dépense'),
                                ('retour', 'Retour'),
                                ('transfer', 'Transfer'),
                                ('virement', 'Virement'),
                                ('versement', 'Versement'),
                                ('encaissement', 'Encaissement'),
                                ('achat', 'Achat'),
                                ('decaissement', 'Décaissement'),
                            ], default='recette')

    @api.model
    def _default_boxe_id(self):
        boxes = self.env['sm_boxes.boxes'].search([], limit=2)
        return boxes.id if len(boxes) == 1 else False

    boxe_id = fields.Many2one(
        comodel_name="sm_boxes.boxes",
        string="Compte",
        required=True,
        default=_default_boxe_id,
    )
    company_id = fields.Many2one('res.company', 'Société', related='boxe_id.company_id',store=True)

    name = fields.Char(string="Motif", required=True, )
    user_id = fields.Many2one('res.users', string='Vendeur',default=lambda self: self.env.user ) # ,track_visibility='onchange', track_sequence=2 
    amount = fields.Float(string="Montant",  required=True, tracking=True, )
    amount_done = fields.Float(string='Montant', compute='_amount_done', store='true')
    mode = fields.Selection(string="Mode", selection=[
                            ('sold', 'Espèce'),
                            ('bank', 'Chèque'),
                            ('virement', 'Virement'),
                            ('versement', 'Versement'),
                            ],
                            required=True, default='sold')


    reference = fields.Char(string="Référence", required=False, )
    order_id = fields.Many2one('sm_sales.order', string='Commande', copy=False, readonly=True, )
    # state = fields.Selection(related='order_id.state', string='Etat', store=True, readonly=True)

    partner_id = fields.Many2one('sm_sales.partner', string="Client/Fournis." )

    @api.model
    def _mail_get_partner_fields(self, introspect_fields=False):
        """partner_id pointe vers sm_sales.partner (modèle personnalisé, pas res.partner),
        et ne doit donc pas être utilisé par le framework de messagerie comme champ res.partner."""
        return []
    
    
    date = fields.Date(string="Date Opération", required=True, default=lambda self:fields.Date.today())


    # débit (-), crédit (+)
    sens = fields.Selection(string="Sens", selection=[
                                ('debit', 'Débit'),
                                ('credit', 'Crédit'), ],
                                required=True, )
    @api.depends('amount', 'sens')
    def _amount_done(self):
        for rec in self:
            rec.amount_done = rec.amount if rec.sens=='credit' else -1*rec.amount

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        box_balances = {}
        for vals in vals_list:
            operation = vals.get('operation') or self.env.context.get('default_operation') or 'recette'
            if operation in ['decaissement', 'achat']:
                boxe_id = vals.get('boxe_id') or self.env.context.get('default_boxe_id') or self._default_boxe_id()
                if boxe_id:
                    boxe = boxe_id if isinstance(boxe_id, models.Model) else self.env['sm_boxes.boxes'].browse(boxe_id)
                    amount = float(vals.get('amount') or 0.0)
                    if not boxe.can_be_negatif:
                        current_sold = box_balances.get(boxe.id, boxe.boxe_sold)
                        if amount > current_sold:
                            raise ValidationError(
                                _("Impossible d'ajouter cette opération : le montant demandé (%(amount).2f) dépasse le solde disponible (%(sold).2f) du compte '%(boxe)s'.") % {
                                    'amount': amount,
                                    'sold': current_sold,
                                    'boxe': boxe.name,
                                }
                            )
                        box_balances[boxe.id] = current_sold - amount
        return super().create(vals_list)

    @api.constrains('operation', 'boxe_id', 'amount')
    def _check_boxe_sold(self):
        for rec in self:
            if rec.operation in ['decaissement', 'achat'] and rec.boxe_id and not rec.boxe_id.can_be_negatif:
                # Dans un constrains, l'impact de l'enregistrement (rec.amount_done) est déjà inclus dans rec.boxe_id.boxe_sold.
                # Le solde disponible avant cette opération est donc : rec.boxe_id.boxe_sold - rec.amount_done.
                solde_disponible = rec.boxe_id.boxe_sold - rec.amount_done
                if rec.amount > solde_disponible:
                    raise ValidationError(
                        _("Impossible d'enregistrer cette opération : le montant demandé (%(amount).2f) dépasse le solde disponible (%(sold).2f) du compte '%(boxe)s'.") % {
                            'amount': rec.amount,
                            'sold': solde_disponible,
                            'boxe': rec.boxe_id.name,
                        }
                    )


   