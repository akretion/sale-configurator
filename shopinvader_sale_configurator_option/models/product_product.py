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
                }
            )

            # Since shopinvader.variant.record_id is a Many2one inherited from
            # product.product, its field is marked as delegate.
            # As delegate fields get a NewId when the record is created
            # (https://github.com/odoo/odoo/blob/15.0/odoo/fields.py#L2783-L2785)
            # we need to disable the delegation otherwise the price computation
            # will fail in case of pricelist because it considers the record.id
            # to be an int:
            # https://github.com/odoo/odoo/blob/15.0/addons/product/models/product_pricelist.py#L94 # noqa

            old_delegate = shopinvader_variant._fields["record_id"].delegate
            shopinvader_variant._fields["record_id"].delegate = False
            shopinvader_variant.record_id = record
            shopinvader_variant._fields["record_id"].delegate = old_delegate

            record.shopinvader_price = shopinvader_variant.price
