# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = ("shopinvader.cart.service",)

    def _prepare_cart_option(self, params_option):
        return {
            "product_id": params_option["product_id"],
            "option_unit_qty": params_option.get("qty", 1),
        }

    def _prepare_cart_item(self, params, cart):
        res = super(CartService, self)._prepare_cart_item(params, cart)
        res["option_ids"] = []
        for op in params.get("options", []):
            res["option_ids"].append((0, 0, self._prepare_cart_option(op)))
        return res

    def _option_validator(self):
        return {
            "product_id": {"coerce": to_int, "required": True},
            "qty": {"coerce": to_int},
        }

    def _validator_add_item(self):
        res = super(CartService, self)._validator_add_item()
        res.update(
            {
                "options": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": self._option_validator(),
                    },
                }
            }
        )
        return res

    def _check_existing_cart_item(self, cart, params):
        # never merge product with options
        # TODO only apply in case of product with options
        return False

    def _play_cart_item_onchanges(self, cart, vals, existing_item=None):
        new_vals = super()._play_cart_item_onchanges(
            cart, vals, existing_item=existing_item
        )
        new_vals.pop("option_ids")
        if "option_ids" in vals:
            new_vals["option_ids"] = vals["option_ids"]
        return new_vals

    def _upgrade_cart_item_quantity(self, cart, item, params, action="replace"):
        vals = self._upgrade_cart_item_quantity_vals(item, params, action=action)
        item.update(vals)
        item.product_uom_change()
