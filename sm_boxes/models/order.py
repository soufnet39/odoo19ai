from odoo import api, models, fields, _
from odoo.tools.misc import str2bool

class SmSalesBoxesOrder(models.Model):
    _inherit = 'sm_sales.order'

    payment_ids = fields.One2many('sm_boxes.operations', 'order_id', string='Paiement', copy=False)
    show_client_payment = fields.Boolean(string="Afficher les paiements",
                               default=lambda self: str2bool(
                                   self.env['ir.config_parameter'].sudo().get_param(
                                       'sm_boxes.show_client_payment')))
    show_supplier_payment = fields.Boolean(string="Afficher les paiements",
                               default=lambda self: str2bool(
                                   self.env['ir.config_parameter'].sudo().get_param(
                                       'sm_boxes.show_supplier_payment')))
    total_reglement = fields.Float(string='Total Règlements',digits="montant", store=True, compute='_compute_total_reglement')

    amount_rest = fields.Float(string='Reste à payer',digits="montant", compute='_compute_total_reglement', store=True)
    
    @api.depends('payment_ids', 'order_lines', 'amount_ttc') #
    def _compute_total_reglement(self):
        for rec in self:
            tot = sum(line.amount for line in rec.payment_ids)
            rec.update({
                'total_reglement': tot,
                'amount_rest': rec.amount_ttc - tot,
            })
