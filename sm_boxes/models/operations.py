from odoo import api, models, fields, _

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
                                ('decaissement', 'Décaissement'),], default='recette'
                            )
    boxe_id = fields.Many2one(comodel_name="sm_boxes.boxes", string="Compte", required=True, )
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

   