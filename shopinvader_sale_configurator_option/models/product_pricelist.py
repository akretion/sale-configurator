# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def get_product_price_rule(
        self, product, quantity, partner, date=False, uom_id=False
    ):
        # The following line will convert NewId with origin to normal record
        product = self.env["product.product"].browse(product.ids)
        return super().get_product_price_rule(
            product, quantity, partner, date=date, uom_id=uom_id
        )
