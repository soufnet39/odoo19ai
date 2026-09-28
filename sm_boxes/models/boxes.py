# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SmBoxesBoxes(models.Model):
    _name = 'sm_boxes.boxes'
    _description = 'Caisses et comptes financiers'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char(string="Compte",  required=True, translate=True, index=True, tracking=1)
    active = fields.Boolean(string='Actif', default=True)

    company_id = fields.Many2one('res.company', 'Société', default=lambda self: self.env.company, index=True)
    boxe_type = fields.Selection(string="Type", selection=[  ('bank',  'Banque'),  ('sold',  'Espèce') ], required=True,default='sold', tracking=2) 

    user_ids = fields.Many2many(comodel_name="res.users", string="Résponsables", )

    rib = fields.Char(string="RIB", required=False, )
    bank_id = fields.Many2one("sm_sales.bank")

    can_be_negatif = fields.Boolean(string="Compte negatif", default=False  )

    operations_ids = fields.One2many('sm_boxes.operations', 'boxe_id')
    boxe_sold = fields.Float(string="Solde", compute='_compute_boxe_sold', store=True)

    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Le nom de compte doit être unique. Veuillez choisir un autre nom.',
    )

    @api.depends('operations_ids.amount_done')
    def _compute_boxe_sold(self):
        for rec in self:
            rec.boxe_sold = sum(rec.operations_ids.mapped('amount_done'))

    def action_view_operations(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('sm_boxes.sm_boxes_operations_action')
        action['name'] = _('Opérations')
        action['domain'] = [('boxe_id', '=', self.id)]
        action['context'] = dict(self.env.context, default_boxe_id=self.id)
        list_view = self.env.ref('sm_boxes.sm_boxes_operations_view_list', raise_if_not_found=False)
        form_view = self.env.ref('sm_boxes.sm_boxes_operations_view_form', raise_if_not_found=False)
        if list_view and form_view:
            action['views'] = [(list_view.id, 'list'), (form_view.id, 'form')]
        return action
   



