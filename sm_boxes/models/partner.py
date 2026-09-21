from odoo import api, models, fields, _

class SmBoxesPartner(models.Model):
    _inherit = 'sm_sales.partner'

    client_operations = fields.One2many('sm_boxes.operations', 'partner_id')

    sold_client = fields.Float(string='Solde client', compute='_calcule_sold_client', store=True )


    @api.depends('client_operations.amount_done')
    def _calcule_sold_client(self):
        for rec in self:
            vl = sum(vi['amount_done'] for vi in rec.client_operations)
            rec.update({'sold_client': vl})

    # La fonction ci-dessous est dupliquée dans sm_boxes.operations

    def sold_client_function(self):
        tree_view_id = self.env.ref('sm_boxes.sm_boxes_operations_list_view').ids
        search_view_id = self.env.ref('sm_boxes.sm_boxes_operations_search_view').ids
        form_view_id = self.env.ref('sm_boxes.sm_boxes_operations_form_view').ids
        # TODO : search_view_id ne fonctionne pas correctement
        return {
            'views': [[tree_view_id, 'tree'], [form_view_id, 'form'], [search_view_id, 'search']],
            'name': _('Opérations'),
            'view_mode': 'list',
            'res_model': 'sm_boxes.operations',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [("partner_id", '=', self.id)]
        }