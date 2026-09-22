from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool


class SmSalesOrder(models.Model):
    _name = "sm_sales.order"
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _description = "Commande client"
    _order = 'id desc, date desc'

        
    @api.depends('order_lines.price_total', 'remise_exist', 'remise_methode', 'remise_taux', 'remise_mta', 'tva_enabled', 'tva_taux', 'mode_paiement_id')
    def _amount_all(self):
        for order in self:
            amount_ht = amount_tva = remise_valeur = amount_ht_before_remise = 0.0

            for line in order.order_lines:
                
                amount_ht_before_remise += line.price_total
                amount_ht += line.price_total

            if order.remise_exist :
                if order.remise_methode == 'taux':
                    remise_valeur = round(amount_ht * order.remise_taux/100,2)
                    amount_ht = amount_ht-remise_valeur
                if order.remise_methode == 'mta':
                    remise_valeur = order.remise_mta
                    amount_ht=amount_ht-remise_valeur

            if order.tva_enabled:
                amount_tva = round(amount_ht * (order.tva_taux / 100),2)

           

            order.update({
                'remise_valeur': remise_valeur,
                'amount_ht_before_remise': amount_ht_before_remise,
                'amount_ht': amount_ht,
                'amount_tva': amount_tva,
                'amount_ttc': amount_ht + amount_tva ,
            })

    name = fields.Char(string='Commande', required=True, copy=False, index=True, default='_< Nouveau >_',)

    name_updatable = fields.Boolean(string="Numero Modifiable", store=False, default=False)
    

    order_lines = fields.One2many('sm_sales.order.line', 'order_id', string='Un article', copy=True, )
    order_lines_count = fields.Integer('Nombre de lignes',store=True, compute='_compute_lines_count' ,default=0)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('canceled', 'Annulée'),],
        string='Etat', readonly=True, copy=False, index=True, tracking=3,
        default='draft', required=True )

    operation_type = fields.Selection([
        ('order', 'Cmd. Vente'), 
        ('purchase', 'Cmd Achat')],
                    string='Type operation',
                    copy=True, )
    date = fields.Date(string='Date', index=True, copy=False, default=fields.Date.today, tracking=4)

    user_id = fields.Many2one('res.users', string='Vendeur', index=True, tracking=2, default=lambda self: self.env.user)

    partner_id = fields.Many2one('sm_sales.partner', string='Client',
            index=True, tracking=1, )  # required in views
    can_change_product_designation_on_sales = fields.Boolean(string="Modifier la désignation", store=False,
                                default=lambda self: str2bool(self.env['ir.config_parameter'].sudo().get_param('sm_sales.can_change_product_designation_on_sales', 'False')))
       
    @api.model
    def _mail_get_partner_fields(self, introspect_fields=False):
        """partner_id pointe vers sm_sales.partner (modèle personnalisé, pas res.partner),
        et ne doit donc pas être utilisé par le framework de messagerie comme champ res.partner."""
        return []


    note = fields.Html('Note', )

   
    #### TVA ##################################################################################################
    tva_enabled = fields.Boolean(string="Utiliser la Tva", default=lambda self: self.env['ir.config_parameter'].sudo().get_param('sm_sales.tva_enabled'))
    tva_taux = fields.Float(string="Taux de TVA", digits="Taux de TVA",
                            default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param('sm_sales.tva_taux', '0')))
    ###########################################################################################################

    #### REMISE ###############################################################################################
    remise_exist = fields.Boolean(string="Utiliser les remises", default=lambda self: self.env['ir.config_parameter'].sudo().get_param('sm_sales.remise_exist') == 'True')
    remise_taux = fields.Float(string='Taux de remise',
                               default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param('sm_sales.remise_default_taux', '0')),
                               digits="Taux de remise")
    remise_mta = fields.Float(string='Montant de remise',
                              default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param('sm_sales.remise_default_mta', '0')),
                              digits="Montant de la remise")
    remise_methode = fields.Selection(string="Methode de remise", selection=[('taux', 'Taux'), ('mta', 'Montant')],
                                      required=True,
                                      default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                          'sm_sales.remise_methode', 'taux'))

    remise_valeur = fields.Float(string="Remise", store=True, readonly=True, compute='_amount_all',
                                 digits="Product Price")
    amount_ht_before_remise = fields.Float(string="Montant HT avant remise", store=True,
                                           readonly=True, compute='_amount_all', digits="Product Price")

    ###########################################################################################################
    # Monétaire
    amount_ht = fields.Float(string='Montant HT', store=True, readonly=True, compute='_amount_all',
                             digits="Product Price")
    # Monétaire
    amount_tva = fields.Float(string='TVA', store=True, readonly=True,
                              digits="Product Price", compute='_amount_all')
    # Monétaire
    amount_ttc = fields.Float(string='Total TTC', store=True, readonly=True,
                              digits="Product Price", compute='_amount_all', tracking=6)

   
    company_id = fields.Many2one('res.company', 'Société', default=lambda self: self.env.company)

    product_name_editable = fields.Boolean(string="Désignation éditable",
                            default=lambda self: self.env['ir.config_parameter'].sudo().get_param('sm_sales.product_name_editable') == 'True')


    mode_paiement_id = fields.Many2one('sm_sales.payment.mode', string="Mode de paiement")
    
    @api.depends('order_lines')
    def _compute_lines_count(self):
        for rec in self:
            rec.order_lines_count = len(rec.order_lines)

    # ------------------------------------------------------------------
    # Lien vers les proformas liées (Many2many)
    # ------------------------------------------------------------------
    quotation_ids = fields.Many2many(
        'sm_sales.quotation', string='Proformas liées',
    )
    quotation_count = fields.Integer(
        string='Nombre de proformas',  
        compute='_compute_quotation_count',
    )

    @api.depends('quotation_ids')
    def _compute_quotation_count(self):
        for order in self:
            order.quotation_count = len(order.quotation_ids)

   

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        # Vérifie si confirm_orders_by_default est activé
        confirmed_order_by_default = str2bool(self.env['ir.config_parameter'].sudo().get_param('sm_sales.confirm_orders_by_default', 'False'))
        confirmed_purchase_by_default = str2bool(self.env['ir.config_parameter'].sudo().get_param('sm_sales.confirm_purchase_by_default', 'False'))
        
        for vals in vals_list:
            if vals.get('name', _('_< Nouveau >_')) == _('_< Nouveau >_'):
                operation_type = vals.get('operation_type')
                if operation_type == 'order':
                    vals['name'] = self.env['ir.sequence'].next_by_code('sm_sales.order')
                    # Définit l'état sur confirmé si confirmed_order_by_default est vrai
                    if confirmed_order_by_default and 'state' not in vals:
                        vals['state'] = 'confirmed'                   
                elif operation_type == 'purchase':
                    vals['name'] = self.env['ir.sequence'].next_by_code('sm_sales.order.purchase')
                    # Définit l'état sur confirmé si confirmed_purchase_by_default est vrai
                    if confirmed_purchase_by_default and 'state' not in vals:
                        vals['state'] = 'confirmed'  

                # else:
                #     vals['name'] = self.env['ir.sequence'].next_by_code('sm_sales.order')
            
            

        return super().create(vals_list)

    def action_confirm(self):
        qtys = sum(l.qty for l in self.order_lines)
        if qtys <= 0 :
            raise UserError(_('Les quantités sont nuls, Pas de confirmation '))
        else:
            self.update({
                'state': 'confirmed',
                'date': fields.Date.today(),
            })
            return True

    def action_cancel(self):
        self.update({
            'state': 'canceled',
        })
        return True

    def action_draft(self):
        self.update({
            'state': 'draft'            
        })
        return True


   
    def print_order(self):
        return self.env.ref('sm_sales.action_report_order').report_action(self)

    # ------------------------------------------------------------------
    # Smart-button : voir les proformas liées
    # ------------------------------------------------------------------
    def action_view_quotations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Proformas liées'),
            'res_model': 'sm_sales.quotation',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.quotation_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

   
   
    
# ########################################################################################################################
# ########################################################################################################################
# ########################################################################################################################

class SmSaleOrderLine(models.Model):
    _name = 'sm_sales.order.line'
    _description = 'Lignes de commande'
    _order = 'order_id, sequence, id'

    @api.depends('unit_price', 'qty')
    def _haseb(self):
        for line in self:
            line.price_total=line.unit_price*line.qty

    sequence = fields.Integer(string='Séquence', default=10)
    order_id = fields.Many2one('sm_sales.order', string='Référence de commande',
                                ondelete='cascade',
                               index=True, copy=False, readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.order_id.operation_type == 'order':
            self.name = self.product_id.name
            self.price_list_price_id = False
            if not self.product_id.use_price_list:
                self.unit_price = self.product_id.default_price
            else:
                self.unit_price = 0.0

    @api.onchange('price_list_price_id')
    def _onchange_price_list_price_id(self):
        if self.price_list_price_id:
            self.unit_price = self.price_list_price_id.price

    company_id = fields.Many2one('res.company', 'Société', related='order_id.company_id',store=True)
    product_id = fields.Many2one('sm_sales.product', string='Produit',  change_default=True, ondelete='restrict',domain=[('sale_ok', '=', True)]) 
    image_128 = fields.Image(string='Image', related='product_id.image_128')

    name = fields.Text(string='Désignation', required=True)
    unit_price = fields.Float('Prix Unit.', required=True, default=0.0,
                              digits="Product Price")
    price_list_price_id = fields.Many2one(
        'sm_sales.pricelist.price', string='Liste de prix',
        domain="[('product_id', '=', product_id)]",
        store=True,
    )
    use_price_list = fields.Boolean(related='product_id.use_price_list', store=True)
    qty = fields.Float(string='Qte.', digits="Quantity", default=1.0 )
    

    price_total = fields.Float(compute='_haseb', string='Total', digits="Product Price", default=0.0, store=True)

    product_code = fields.Char(string="Réf.", related='product_id.code')
    product_categ_id = fields.Many2one(string="Catégorie", related='product_id.categ_id', store=True)


    user_id = fields.Many2one(related='order_id.user_id', store=True, string='Vendeur', readonly=True)
    partner_id = fields.Many2one(related='order_id.partner_id', string='Client',    readonly=False, store=True)
    operation_type = fields.Selection(string="Type d'opération", related='order_id.operation_type',store=True )
    product_type = fields.Selection(related='product_id.product_type')
      

   