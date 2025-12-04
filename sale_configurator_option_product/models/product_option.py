# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()
        for prod in self:
            option_line_ids = prod.sale_line_id.child_option_ids.filtered(
                lambda o: o.product_id.type == "consu"
            )
            for line in option_line_ids:
                moves.append(
                    prod._get_move_raw_values(
                        line.product_id, line.product_uom_qty, line.product_uom
                    )
                )

        return moves
