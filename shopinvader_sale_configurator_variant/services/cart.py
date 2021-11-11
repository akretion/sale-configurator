# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _prepare_cart_variant(self, params_variant):
        return {
            "product_id": params_variant["product_id"],
            "product_uom_qty": params_variant["qty"],
        }

    def _prepare_cart_item(self, params, cart):
        if "variants" in params:
            product = self.env["product.product"].browse(
                params["variants"][0]["product_id"]
            )
            # we need to set a product id to avoid
            # - breaking call to super
            # - having an empty field product_id that is required in natif odoo
            params.update(
                {
                    "product_id": product.id,
                    "item_qty": 1,
                }
            )
        res = super()._prepare_cart_item(params, cart)
        if "variants" in params:
            res.update(
                {
                    "is_multi_variant_line": True,
                    "variant_ids": [
                        (0, 0, self._prepare_cart_variant(variant))
                        for variant in params.get("variants", [])
                    ],
                    "product_tmpl_id": product.product_tmpl_id.id,
                }
            )
        return res

    def add_multi_variant_item(self, **params):
        return self.add_item(**params)

    def update_multi_variant_item(self, **params):
        return self.update_item(**params)

    def _get_variants_schema(self):
        return {
            "variants": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "product_id": {"coerce": to_int, "required": True},
                        "qty": {"coerce": to_int},
                    },
                },
            }
        }

    def _validator_add_multi_variant_item(self):
        res = self._validator_add_item()
        for key in ["product_id", "item_qty"]:
            res.pop(key)
        res.update(self._get_variants_schema())
        return res

    def _validator_update_multi_variant_item(self):
        res = self._validator_update_item()
        res.pop("item_qty")
        res.update(self._get_variants_schema())
        return res

    def _check_allowed_product(self, cart, params):
        if "variants" in params:
            for params_variant in params["variants"]:
                super()._check_allowed_product(cart, params_variant)
            products = self.env["product.product"].browse(
                [v["product_id"] for v in params["variants"]]
            )
            if len(products.product_tmpl_id) > 1:
                raise UserError(_("All variant should belong to the same model"))
        else:
            super()._check_allowed_product(cart, params)

    def _get_sale_order_line_name(self, vals):
        if vals.get("is_multi_variant_line"):
            return self.env["product.template"].browse(vals["product_tmpl_id"]).name
        else:
            return super()._get_sale_order_line_name(vals)

    def _check_existing_cart_item(self, cart, params):
        if "variants" in params:
            return False
        else:
            lines = super()._check_existing_cart_item(cart, params)
            if lines:
                return lines.filtered(lambda l: not l.is_multi_variant_line)
            else:
                return lines

    def _upgrade_cart_item_quantity_vals(self, item, params, action="replace"):
        if "variants" in params:
            # Put a default value as qty to avoid break the call to super
            # this have no impact as the real qty will be computed
            params["item_qty"] = 1
        vals = super()._upgrade_cart_item_quantity_vals(item, params, action=action)
        if "variants" in params:
            vals.pop("product_uom_qty")
            if action == "replace":
                item.variant_ids.unlink()
                vals["variant_ids"] = [
                    (0, 0, self._prepare_cart_variant(variant))
                    for variant in params["variants"]
                ]
            else:
                raise UserError(_("sum action Not supported with variants"))
        return vals
