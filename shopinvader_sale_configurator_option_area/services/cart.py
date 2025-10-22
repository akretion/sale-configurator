# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _get_vals_for_product_option(self, product_option):
        res = super()._get_vals_for_product_option(product_option)
        res["option_area_id"] = product_option.area_id.id
        return res
