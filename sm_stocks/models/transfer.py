# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SmStocksTransfer(models.Model):
    _name = 'sm_stocks.transfer'
    _description = 'Transfert entre stocks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Numéro',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('Nouveau'),
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )
    stock_source_id = fields.Many2one(
        'sm_stocks.stock',
        string='Stock source',
        required=True,
        tracking=True,
    )
    stock_dest_id = fields.Many2one(
        'sm_stocks.stock',
        string='Stock destination',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('done', 'Transféré'),
            ('cancel', 'Annulé'),
        ],
        string='État',
        default='draft',
        required=True,
        tracking=True,
        copy=False,
    )
    line_ids = fields.One2many(
        'sm_stocks.transfer.line',
        'transfer_id',
        string='Articles',
        copy=True,
    )
    note = fields.Text(string='Notes')

    lines_count = fields.Integer(
        string="Nombre d'articles",
        compute='_compute_lines_count',
    )

    @api.depends('line_ids')
    def _compute_lines_count(self):
        for transfer in self:
            transfer.lines_count = len(transfer.line_ids)

    @api.constrains('stock_source_id', 'stock_dest_id')
    def _check_stocks_different(self):
        for transfer in self:
            if transfer.stock_source_id and transfer.stock_dest_id and transfer.stock_source_id == transfer.stock_dest_id:
                raise ValidationError(_("Le stock source et le stock destination doivent être différents."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sm_stocks.transfer') or _('Nouveau')
        return super().create(vals_list)

    def action_validate(self):
        for transfer in self:
            if transfer.state != 'draft':
                continue
            if not transfer.line_ids:
                raise UserError(_("Veuillez ajouter au moins un article à transférer."))
            if transfer.stock_source_id == transfer.stock_dest_id:
                raise ValidationError(_("Le stock source et le stock destination doivent être différents."))

            # Group requested quantities by product
            qty_by_product = {}
            for line in transfer.line_ids:
                if line.qty <= 0:
                    raise ValidationError(
                        _("La quantité pour l'article '%s' doit être supérieure à zéro.") % line.product_id.name
                    )
                qty_by_product[line.product_id] = qty_by_product.get(line.product_id, 0.0) + line.qty

            # Verify availability in source stock if negative stock is not allowed
            if not transfer.stock_source_id.can_be_negatif:
                for product, req_qty in qty_by_product.items():
                    if product.product_type == 'service':
                        continue
                    available = product.with_context(stock_id=transfer.stock_source_id.id).rest_in_stock
                    if req_qty > available:
                        raise ValidationError(
                            _("Stock insuffisant pour l'article '%(product)s' dans le stock source '%(stock)s'.\n"
                              "Disponible : %(avail)s | Demandé : %(req)s") % {
                                'product': product.name,
                                'stock': transfer.stock_source_id.name,
                                'avail': int(available) if available.is_integer() else available,
                                'req': int(req_qty) if req_qty.is_integer() else req_qty,
                            }
                        )

            transfer.state = 'done'

    def action_cancel(self):
        for transfer in self:
            if transfer.state == 'done':
                # Check if destination stock can afford returning items if it cannot be negative
                if not transfer.stock_dest_id.can_be_negatif:
                    qty_by_product = {}
                    for line in transfer.line_ids:
                        qty_by_product[line.product_id] = qty_by_product.get(line.product_id, 0.0) + line.qty
                    for product, req_qty in qty_by_product.items():
                        if product.product_type == 'service':
                            continue
                        available = product.with_context(stock_id=transfer.stock_dest_id.id).rest_in_stock
                        if req_qty > available:
                            raise ValidationError(
                                _("Impossible d'annuler ce transfert : le stock destination '%(stock)s' "
                                  "ne dispose pas d'assez d'exemplaires de '%(product)s' "
                                  "(Disponible : %(avail)s | Nécessaire : %(req)s).") % {
                                    'stock': transfer.stock_dest_id.name,
                                    'product': product.name,
                                    'avail': int(available) if available.is_integer() else available,
                                    'req': int(req_qty) if req_qty.is_integer() else req_qty,
                                }
                            )
            transfer.state = 'cancel'

    def action_draft(self):
        for transfer in self:
            if transfer.state == 'cancel':
                transfer.state = 'draft'

    def unlink(self):
        for transfer in self:
            if transfer.state == 'done':
                raise UserError(_("Vous ne pouvez pas supprimer un transfert validé. Veuillez d'abord l'annuler."))
        return super().unlink()


class SmStocksTransferLine(models.Model):
    _name = 'sm_stocks.transfer.line'
    _description = 'Ligne de transfert entre stocks'
    _order = 'id asc'

    transfer_id = fields.Many2one(
        'sm_stocks.transfer',
        string='Transfert',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        'sm_sales.product',
        string='Article',
        required=True,
        domain="[('product_type', '!=', 'service')]",
    )
    stock_source_id = fields.Many2one(
        'sm_stocks.stock',
        string='Stock source',
        related='transfer_id.stock_source_id',
        store=True,
        readonly=True,
    )
    stock_dest_id = fields.Many2one(
        'sm_stocks.stock',
        string='Stock destination',
        related='transfer_id.stock_dest_id',
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        related='transfer_id.state',
        string='État',
        store=True,
        readonly=True,
    )
    date = fields.Date(
        related='transfer_id.date',
        string='Date',
        store=True,
        readonly=True,
    )
    rest_in_stock = fields.Float(
        string='Dispo source',
        compute='_compute_rest_in_stock',
        digits='Quantity',
    )
    qty = fields.Float(
        string='Quantité',
        required=True,
        default=1.0,
        digits='Quantity',
    )

    @api.depends('product_id', 'transfer_id.stock_source_id')
    def _compute_rest_in_stock(self):
        for line in self:
            if line.product_id and line.transfer_id.stock_source_id:
                line.rest_in_stock = line.product_id.with_context(
                    stock_id=line.transfer_id.stock_source_id.id
                ).rest_in_stock
            else:
                line.rest_in_stock = 0.0

    @api.onchange('product_id', 'qty')
    def _onchange_check_qty(self):
        if self.product_id and self.transfer_id.stock_source_id:
            source_stock = self.transfer_id.stock_source_id
            if not source_stock.can_be_negatif and self.qty > self.rest_in_stock:
                return {
                    'warning': {
                        'title': _("Stock insuffisant"),
                        'message': _(
                            "Attention : La quantité demandée (%(qty)s) dépasse la quantité disponible (%(rest)s) "
                            "dans le stock source '%(stock)s'."
                        ) % {
                            'qty': int(self.qty) if self.qty.is_integer() else self.qty,
                            'rest': int(self.rest_in_stock) if self.rest_in_stock.is_integer() else self.rest_in_stock,
                            'stock': source_stock.name,
                        }
                    }
                }

    @api.constrains('qty')
    def _check_qty_positive(self):
        for line in self:
            if line.qty <= 0:
                raise ValidationError(_("La quantité à transférer doit être strictement positive."))
