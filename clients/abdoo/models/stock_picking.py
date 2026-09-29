# -*- coding: utf-8 -*-
from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """Auto-set done quantity = ordered quantity before validation.

        Applies to all picking types (sales delivery, purchase receipt, etc.).
        Only touches moves that are not already done or cancelled.
        """
        for picking in self:
            for move in picking.move_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')
            ):
                move.quantity = move.product_uom_qty
        return super().button_validate()
