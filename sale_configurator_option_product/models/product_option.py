# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()
        moves_temp = []
        for prod in self:
            moves_temp = self.env["sale.order.line"].read_group(
                [
                    ("product_id.type", "=", "product"),
                    ("id", "in", prod.sale_line_ids.option_ids.ids),
                ],
                fields=["product_uom_qty:sum"],
                groupby=["product_id", "product_uom"],
                lazy=False,
            )
            for lines in moves_temp:
                moves.append(
                    prod._get_move_raw_values(
                        self.env["product.product"].browse(lines["product_id"][0]),
                        lines["product_uom_qty"],
                        self.env["uom.uom"].browse(lines["product_uom"][0]),
                    )
                )
        return moves
