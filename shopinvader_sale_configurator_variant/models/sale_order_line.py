# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # Playing the onchange on variant_ids is useless and broken so don't do it
    def play_onchanges(self, vals, fields):
        fields = [field for field in fields if field != "variant_ids"]
        variant_ids = vals.pop("variant_ids", None)
        res = super().play_onchanges(vals, fields)
        # restore original variant_ids values
        if variant_ids is not None:
            res["variant_ids"] = variant_ids
        else:
            res.pop("variant_ids", None)
        return res
