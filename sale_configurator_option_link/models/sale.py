# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _set_included_options(self):
        sale_options = self.option_ids.mapped("product_option_id")
        included_option = sale_options.mapped("included_option_ids")
        to_include = included_option - sale_options
        options = []
        for opt in to_include:
            options.append((0, 0, self._prepare_sale_line_option(opt)))
        self.option_ids = options
        return to_include

    @api.onchange("option_ids")
    def option_id_change(self):
        res = {}
        if self.option_ids:
            self._set_included_options()
        return res
