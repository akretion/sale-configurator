# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _prepare_cart_option(self, params_option):
        cart_option = super()._prepare_cart_option(params_option)
        if "message" in params_option:
            cart_option.update(
                {
                    "option_message": params_option["message"],
                }
            )
        return cart_option

    def _get_options_schema(self):
        schema = super()._get_options_schema()
        schema["options"]["schema"]["schema"].update(
            {
                "message": {"type": "string"},
            }
        )
        return schema
