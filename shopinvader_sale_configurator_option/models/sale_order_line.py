# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Playing the onchange on option_ids is useless and broken so don't do it
    def play_onchanges(self, vals, fields):
        fields = [field for field in fields if field != "option_ids"]
        option_ids = vals.pop("option_ids", None)
        res = super().play_onchanges(vals, fields)
        # restore original option_ids values
        if option_ids is not None:
            res["option_ids"] = option_ids
        else:
            res.pop("option_ids", None)
        return res
