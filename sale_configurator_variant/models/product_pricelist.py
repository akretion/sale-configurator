# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def get_product_price_rule(
        self, product, quantity, partner, date=False, uom_id=False
    ):
        if self._context.get("parent_variant_qty"):
            quantity = self._context["parent_variant_qty"]
        return super().get_product_price_rule(
            product, quantity, partner, date=date, uom_id=uom_id
        )
