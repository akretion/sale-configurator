# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_pos_line(self):
        return self.order_line.filtered(lambda s: not s.parent_option_id)

    def _prepare_pos_json_line_option(self, option_sol):
        option = (
            option_sol.parent_option_id.product_id.configurable_option_ids.filtered(
                lambda o: o.product_id == option_sol.product_id
            )
        )
        # TODO FIXME IN V14 option_sol.product_option_id.id
        return {
            "id": option.id,
            "product_id": option_sol.product_id.id,
            "description": option_sol.name,
            "quantity": option_sol.option_unit_qty,
            "price": option_sol.price_unit,
            "notes": "",  # note have been merged into description
        }

    def _prepare_pos_json_line(self, line):
        res = super()._prepare_pos_json_line(line)
        options = []
        if line.option_ids:
            options = [
                self._prepare_pos_json_line_option(option) for option in line.option_ids
            ]
            res["config"] = {"selected_options": options}
        return res
