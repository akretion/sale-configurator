# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = ("shopinvader.cart.service",)

    def _get_vals_for_product_option(self, product_option):
        return {"product_id": product_option.product_id.id}

    def _prepare_cart_option(self, params_option):
        opt = self.env["product.configurator.option"].browse(params_option["option_id"])
        res = self._get_vals_for_product_option(opt)
        res["option_unit_qty"] = params_option.get("qty", 1)
        return res

    def _prepare_cart_item(self, params, cart):
        res = super(CartService, self)._prepare_cart_item(params, cart)
        res["option_ids"] = []
        for op in params.get("options", []):
            res["option_ids"].append((0, 0, self._prepare_cart_option(op)))
        return res

    def _get_options_schema(self):
        return {
            "options": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "option_id": {"coerce": to_int, "required": True},
                        "qty": {"coerce": to_int},
                    },
                },
            }
        }

    def _validator_add_item(self):
        res = super()._validator_add_item()
        res.update(self._get_options_schema())
        return res

    def _validator_update_item(self):
        res = super()._validator_update_item()
        res.update(self._get_options_schema())
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

    def _upgrade_cart_item_quantity_vals(self, item, params, action="replace"):
        vals = super()._upgrade_cart_item_quantity_vals(item, params, action=action)
        assert action in ("sum", "replace")
        if "options" in params:
            if action == "replace":
                vals["option_ids"] = [(5, 0, 0)]
            else:
                raise UserError(_("sum action Not supported with options"))
            for op in params.get("options", []):
                vals["option_ids"].append((0, 0, self._prepare_cart_option(op)))
        return vals

    # TODO FIXME incorrect inherit
    def _upgrade_cart_item_quantity(self, cart, item, params, action="replace"):
        vals = self._upgrade_cart_item_quantity_vals(item, params, action=action)
        item.update(vals)
        item.product_uom_change()
