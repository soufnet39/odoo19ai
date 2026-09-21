# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import str2bool


class SmInvoice(models.Model):
    _name = "sm_invoices.invoice"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Facture client"
    _order = 'id desc, date desc'

    # ------------------------------------------------------------------
    # Totaux calculés
    # ------------------------------------------------------------------
    @api.depends(
        'invoice_lines.price_total',
        'remise_exist', 'remise_methode', 'remise_taux', 'remise_mta',
        'tva_enabled', 'tva_taux',
        'mode_paiement_id',
    )
    def _amount_all(self):
        for invoice in self:
            amount_ht = amount_tva = remise_valeur = amount_ht_before_remise = 0.0

            for line in invoice.invoice_lines:
                amount_ht_before_remise += line.price_total
                amount_ht += line.price_total

            if invoice.remise_exist:
                if invoice.remise_methode == 'taux':
                    remise_valeur = round(amount_ht * invoice.remise_taux / 100, 2)
                    amount_ht = amount_ht - remise_valeur
                if invoice.remise_methode == 'mta':
                    remise_valeur = invoice.remise_mta
                    amount_ht = amount_ht - remise_valeur

            if invoice.tva_enabled:
                amount_tva = round(amount_ht * (invoice.tva_taux / 100), 2)

            invoice.update({
                'remise_valeur': remise_valeur,
                'amount_ht_before_remise': amount_ht_before_remise,
                'amount_ht': amount_ht,
                'amount_tva': amount_tva,
                'amount_ttc': amount_ht + amount_tva,
            })

    # ------------------------------------------------------------------
    # Champs d'en-tête
    # ------------------------------------------------------------------
    name = fields.Char(
        string='Facture', required=True, copy=False, index=True,
        default=_('_< Nouveau >_'),
    )

    name_updatable = fields.Boolean(string="Numero Modifiable", store=False, default=False)

    invoice_lines = fields.One2many(
        'sm_invoices.invoice.line', 'invoice_id',
        string='Lignes', copy=True,
    )
    invoice_lines_count = fields.Integer(
        'Nombre de lignes', store=True,
        compute='_compute_lines_count', default=0,
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('canceled', 'Annulée'),
    ], string='Etat', readonly=True, copy=False, index=True, tracking=3,
        default='draft', required=True)

    date = fields.Date(
        string='Date', index=True, copy=False,
        default=fields.Date.today, tracking=4,
    )

    user_id = fields.Many2one(
        'res.users', string='Vendeur', index=True, tracking=2,
        default=lambda self: self.env.user,
    )

    partner_id = fields.Many2one(
        'sm_sales.partner', string='Client',
        index=True, tracking=1,
    )  # requis dans les vues

    can_change_product_designation_on_invoices = fields.Boolean(
        string="Modifier la désignation", store=False,
        default=lambda self: str2bool(
            self.env['ir.config_parameter'].sudo().get_param(
                'sm_invoices.can_change_product_designation_on_invoices', 'False'
            )
        ),
    )

    @api.model
    def _mail_get_partner_fields(self, introspect_fields=False):
        """partner_id pointe vers sm_sales.partner (modèle personnalisé, pas res.partner),
        et ne doit donc pas être utilisé par le framework de messagerie comme champ res.partner."""
        return []

    note = fields.Html('Note')

    # ------------------------------------------------------------------
    # TVA
    # ------------------------------------------------------------------
    tva_enabled = fields.Boolean(
        string="Utiliser la Tva",
        default=lambda self: str2bool(
            self.env['ir.config_parameter'].sudo().get_param(
                'sm_invoices.tva_enabled', 'False'
            )
        ),
    )
    tva_taux = fields.Float(
        string="Taux de TVA", digits="Taux de TVA",
        default=lambda self: float(
            self.env['ir.config_parameter'].sudo().get_param('sm_invoices.tva_taux', '0')
        ),
    )

    # ------------------------------------------------------------------
    # Remise
    # ------------------------------------------------------------------
    remise_exist = fields.Boolean(
        string="Utiliser les remises",
        default=lambda self: str2bool(
            self.env['ir.config_parameter'].sudo().get_param(
                'sm_invoices.remise_exist', 'False'
            )
        ),
    )
    remise_taux = fields.Float(
        string='Taux de remise',
        default=lambda self: float(
            self.env['ir.config_parameter'].sudo().get_param('sm_invoices.remise_default_taux', '0')
        ),
        digits="Taux de remise",
    )
    remise_mta = fields.Float(
        string='Montant de remise',
        default=lambda self: float(
            self.env['ir.config_parameter'].sudo().get_param('sm_invoices.remise_default_mta', '0')
        ),
        digits="Montant de la remise",
    )
    remise_methode = fields.Selection(
        string="Methode de remise",
        selection=[('taux', 'Taux'), ('mta', 'Montant')],
        required=True,
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'sm_invoices.remise_methode', 'taux'
        ),
    )

    remise_valeur = fields.Float(
        string="Remise", store=True, readonly=True, compute='_amount_all',
        digits="Product Price",
    )
    amount_ht_before_remise = fields.Float(
        string="Montant HT avant remise", store=True,
        readonly=True, compute='_amount_all', digits="Product Price",
    )

    # ------------------------------------------------------------------
    # Totaux
    # ------------------------------------------------------------------
    amount_ht = fields.Float(
        string='Montant HT', store=True, readonly=True, compute='_amount_all',
        digits="Product Price",
    )
    amount_tva = fields.Float(
        string='TVA', store=True, readonly=True,
        digits="Product Price", compute='_amount_all',
    )
    amount_ttc = fields.Float(
        string='Total TTC', store=True, readonly=True,
        digits="Product Price", compute='_amount_all', tracking=6,
    )

    company_id = fields.Many2one(
        'res.company', 'Société', default=lambda self: self.env.company,
    )

    mode_paiement_id = fields.Many2one(
        'me_sales.payment.mode', string="Mode de paiement",
    )

    # ------------------------------------------------------------------
    # Lien vers les commandes (Many2many)
    # ------------------------------------------------------------------
    sale_order_ids = fields.Many2many(
        'sm_sales.order', string='Commandes liées',
        domain="[('operation_type', '=', 'order'), ('state', '=', 'confirmed')]",
    )
    sale_order_count = fields.Integer(
        string='Nombre de commandes', store=True,
        compute='_compute_sale_order_count',
    )

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for invoice in self:
            invoice.sale_order_count = len(invoice.sale_order_ids)

    @api.depends('invoice_lines')
    def _compute_lines_count(self):
        for rec in self:
            rec.invoice_lines_count = len(rec.invoice_lines)

    # ------------------------------------------------------------------
    # Créer — assigne la séquence FACT/
    # ------------------------------------------------------------------
    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('name', _('_< Nouveau >_')) == _('_< Nouveau >_'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sm_invoices.invoice')

        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Actions de workflow
    # ------------------------------------------------------------------
    def action_confirm(self):
        qtys = sum(l.qty for l in self.invoice_lines)
        if qtys <= 0:
            raise UserError(_('Les quantités sont nulles, pas de confirmation.'))
        else:
            self.update({
                'state': 'confirmed',
                'date': fields.Date.today(),
            })
            return True

    def action_cancel(self):
        self.update({'state': 'canceled'})
        return True

    def action_draft(self):
        self.update({'state': 'draft'})
        return True

    def print_invoice(self):
        return self.env.ref('sm_invoices.action_report_invoice').report_action(self)

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


# ##########################################################################
# Lignes de facture
# ##########################################################################
class SmInvoiceLine(models.Model):
    _name = 'sm_invoices.invoice.line'
    _description = 'Lignes de facture'
    _order = 'invoice_id, sequence, id'

    @api.depends('unit_price', 'qty')
    def _haseb(self):
        for line in self:
            line.price_total = line.unit_price * line.qty

    sequence = fields.Integer(string='Séquence', default=10)
    invoice_id = fields.Many2one(
        'sm_invoices.invoice', string='Référence de facture',
        ondelete='cascade', index=True, copy=False, readonly=True,
    )

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

    company_id = fields.Many2one(
        'res.company', 'Société',
        related='invoice_id.company_id', store=True,
    )
    product_id = fields.Many2one(
        'sm_sales.product', string='Produit',
        change_default=True, ondelete='restrict',
        domain=[('sale_ok', '=', True)],
    )
    image_128 = fields.Image(string='Image', related='product_id.image_128')

    name = fields.Text(string='Désignation', required=True)
    unit_price = fields.Float(
        'Prix Unit.', required=True, default=0.0,
        digits="Product Price",
    )
    price_list_price_id = fields.Many2one(
        'sm_sales.pricelist.price', string='Liste de prix',
        domain="[('product_id', '=', product_id)]",
        store=True,
    )
    use_price_list = fields.Boolean(
        related='product_id.use_price_list', store=True,
    )
    qty = fields.Float(string='Qte.', digits="Quantity", default=1.0)

    price_total = fields.Float(
        compute='_haseb', string='Total',
        digits="Product Price", default=0.0, store=True,
    )

    product_code = fields.Char(string="Réf.", related='product_id.code')
    product_categ_id = fields.Many2one(
        string="Catégorie",
        related='product_id.categ_id', store=True,
    )

    user_id = fields.Many2one(
        related='invoice_id.user_id', store=True,
        string='Vendeur', readonly=True,
    )
    partner_id = fields.Many2one(
        related='invoice_id.partner_id',
        string='Client', readonly=False, store=True,
    )
