# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_restricted_qty(self):
        self.ensure_one()
        if self.child_type == "variant":
            return {}
        else:
            return super()._get_sale_restricted_qty()

    @api.onchange("product_tmpl_id")
    def product_tmpl_id_change(self):
        super().product_tmpl_id_change()
        if self.product_tmpl_id:
            self.product_uom = self.product_tmpl_id.uom_id
