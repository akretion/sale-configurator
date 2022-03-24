# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopinvader_price = fields.Serialized(
        compute="_compute_shopinvader_price",
        string="Computed Price for Shopinvader",
        help=(
            "Option are not bind on shopinvader, but this field allow to get "
            "the price in the shopinvader context"
        ),
    )

    def _compute_product_price(self):
        tmp_records = self.filtered(lambda s: isinstance(s.id, models.NewId))
        real_records = self - tmp_records
        if real_records:
            super(ProductProduct, real_records)._compute_product_price()
        if tmp_records:
            for tmp_record in tmp_records:
                tmp_record.price = tmp_record._origin.price

    def _compute_shopinvader_price(self):
        for record in self:
            backend = self._context["shopinvader_backend"]
            # Create a New shopinvader Variant to be able to call native code
            # Even if option are not binded
            shopinvader_variant = self.env["shopinvader.variant"].new(
                {
                    "backend_id": backend.id,
                    "lang_id": backend.lang_ids[0].id,
                    "record_id": record.id,
                }
            )
            record.shopinvader_price = shopinvader_variant.price
