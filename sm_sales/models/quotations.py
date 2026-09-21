from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool


class SmSalesQuotation(models.Model):
    _name = "sm_sales.quotation"
    _inherit = [ 'mail.thread', 'mail.activity.mixin']
    _description = "Proforma client"
    _order = 'id desc, date desc'

        
    @api.depends('quotation_lines.price_total', 'remise_exist', 'remise_methode', 'remise_taux', 'remise_mta', 'tva_enabled', 'tva_taux', 'mode_paiement_id')
    def _amount_all(self):
        for quotation in self:
            amount_ht = amount_tva = remise_valeur = amount_ht_before_remise = 0.0
            for line in quotation.quotation_lines: 
                amount_ht_before_remise += line.price_total
                amount_ht += line.price_total

            if quotation.remise_exist :
                if quotation.remise_methode == 'taux':
                    remise_valeur = round(amount_ht * quotation.remise_taux/100,2)
                    amount_ht = amount_ht-remise_valeur
                if quotation.remise_methode == 'mta':
                    remise_valeur = quotation.remise_mta
                    amount_ht=amount_ht-remise_valeur

            if quotation.tva_enabled:
                amount_tva = round(amount_ht * (quotation.tva_taux / 100),2)

           

            quotation.update({
                'remise_valeur': remise_valeur,
                'amount_ht_before_remise': amount_ht_before_remise,
                'amount_ht': amount_ht,
                'amount_tva': amount_tva,
                'amount_ttc': amount_ht + amount_tva ,
            })

    name = fields.Char(string='Proforma', required=True, copy=False, index=True, default=_('_< Nouveau >_'),)
    # Pour savoir si l'enregistrement est "neuf" (jamais modifié après création),
    # utiliser la comparaison : record.create_date == record.write_date
    # (les deux valent False tant que le record n'est pas persisté).
    name_updatable = fields.Boolean(string="Numero Modifiable", store=False, default=False)


    quotation_lines = fields.One2many('sm_sales.quotation.line', 'quotation_id', string='Un article', copy=True, )
    quotation_lines_count = fields.Integer('Nombre de lignes',store=True, compute='_compute_lines_count' ,default=0)
 
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


    mode_paiement_id = fields.Many2one('me_sales.payment.mode', string="Mode de paiement")
    
    @api.depends('quotation_lines')
    def _compute_lines_count(self):
        for rec in self:
            rec.quotation_lines_count = len(rec.quotation_lines)

    # ------------------------------------------------------------------
    # Lien vers les commandes liées (Many2many)
    # ------------------------------------------------------------------
    sale_order_ids = fields.Many2many(
        'sm_sales.order', string='Commandes liées',
        domain="[('operation_type', '=', 'order'), ('state', '=', 'confirmed')]",
    )
    sales_order_count = fields.Integer(
        string='Nombre de commandes', 
        compute='_compute_sale_order_count',
    )

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for quotation in self:
            quotation.sales_order_count = len(quotation.sale_order_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('_< Nouveau >_')) == _('_< Nouveau >_'):
                vals['name'] = (
                    self.env['ir.sequence'].next_by_code('sm_sales.quotation')
                    or _('_<Nouveau >_')
                )
        return super().create(vals_list)

   
    def print_quotation(self):
        return self.env.ref('sm_sales.action_report_quotation').report_action(self)

    # ------------------------------------------------------------------
    # Convertir la proforma en commande client
    # ------------------------------------------------------------------
    def action_convert_to_order(self):
        self.ensure_one()
        qtys = sum(l.qty for l in self.quotation_lines)
        if qtys <= 0:
            raise UserError(_('Les quantités sont nulles, conversion impossible.'))

        line_vals = []
        for line in self.quotation_lines:
            line_vals.append((0, 0, {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'name': line.name,
                'qty': line.qty,               
                'unit_price': line.unit_price,
                'price_list_price_id': line.price_list_price_id.id if line.price_list_price_id else False,
            }))

        order_vals = {
            'operation_type': 'order',
            'state': 'draft',  # force draft even if sm_sales.confirm_orders_by_default=True
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'user_id': self.user_id.id,
            'tva_enabled': self.tva_enabled,
            'tva_taux': self.tva_taux,
            'remise_exist': self.remise_exist,
            'remise_methode': self.remise_methode,
            'remise_taux': self.remise_taux,
            'remise_mta': self.remise_mta,
            'mode_paiement_id': self.mode_paiement_id.id if self.mode_paiement_id else False,
            'quotation_ids': [(4, self.id)],
            'order_lines': line_vals,
            'document_type':'livraison'
        }

        order = self.env['sm_sales.order'].create(order_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Commande'),
            'res_model': 'sm_sales.order',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }

    # ------------------------------------------------------------------
    # Smart-button : voir les commandes liées
    # ------------------------------------------------------------------
    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes liées'),
            'res_model': 'sm_sales.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

   
   
    
# ########################################################################################################################
# ########################################################################################################################
# ########################################################################################################################

class SmSaleQuotationLine(models.Model):
    _name = 'sm_sales.quotation.line'
    _description = 'Lignes de proforma'
    _order = 'quotation_id, sequence, id'

    @api.depends('unit_price', 'qty')
    def _haseb(self):
        for line in self:
            line.price_total=line.unit_price*line.qty

    sequence = fields.Integer(string='Séquence', default=10)
    quotation_id = fields.Many2one('sm_sales.quotation', string='Référence de proforma',
                                ondelete='cascade',
                               index=True, copy=False, readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
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

    company_id = fields.Many2one('res.company', 'Société', related='quotation_id.company_id',store=True)
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


    user_id = fields.Many2one(related='quotation_id.user_id', store=True, string='Vendeur', readonly=True)
    partner_id = fields.Many2one(related='quotation_id.partner_id', string='Client',    readonly=False, store=True)
    product_type = fields.Selection(related='product_id.product_type')
     

   