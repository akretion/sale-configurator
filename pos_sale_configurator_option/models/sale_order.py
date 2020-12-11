# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_pos_option(self, option):
        if option["notes"]:
            description = "\n".join([option["description"], option["notes"]])
        else:
            description = option["description"]
        return {
            "product_id": int(option["product_id"]),
            "option_unit_qty": int(option["quantity"]),
            "option_qty_type": "proportional_qty",
            "product_option_id": int(option["id"]),
            "name": description,
        }

    def _prepare_pos_line(self, line):
        vals = super()._prepare_pos_line(line)
        if line.get("config", {}).get("selected_options"):
            vals["option_ids"] = []
            for option in line["config"]["selected_options"]:
                vals["option_ids"].append([0, 0, self._prepare_pos_option(option)])
        return vals
