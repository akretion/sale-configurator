# Copyright 2020 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_restricted_qty(self):
        res = super()._get_sale_restricted_qty()
        if self.product_option_id:
            res["sale_min_qty"] = self.product_option_id.sale_min_qty
            res["sale_max_qty"] = self.product_option_id.sale_max_qty
        return res
