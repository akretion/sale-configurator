# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_pos_line(self):
        return self.order_line.filtered(lambda s: not s.parent_id)

    def _prepare_pos_json_line_option(self, line):
        return {
            "id": line.product_option_id.id,
            "product_id": line.product_id.id,
            "description": line.name,
            "qty": line.option_unit_qty,
            "price": line.price_unit,
            "note": line.note,
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
