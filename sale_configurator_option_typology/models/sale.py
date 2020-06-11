# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    option_typology_id = fields.Many2one(
        "product.configurator.option.typology", "Typology"
    )

    @api.onchange("product_option_id")
    def product_option_id_change(self):
        res = super().product_option_id_change()
        res["domain"] = {
            "option_typology_id": [
                ("id", "in", self.product_option_id.typology_ids.ids)
            ]
        }
        return res
