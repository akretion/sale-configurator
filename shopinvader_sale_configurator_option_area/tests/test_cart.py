# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_sale_configurator_option.tests.cart_common import (
    ConfiguratorCartCommonCase,
)


class ConfiguratorCartCase(ConfiguratorCartCommonCase):
    def test_add_item_with_option(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 2)
        area_1 = self.env.ref("sale_configurator_option_area.product_option_area_1")
        area_2 = self.env.ref("sale_configurator_option_area.product_option_area_2")
        self.assertEqual(options[0]["area"]["id"], area_1.id)
        self.assertEqual(options[1]["area"]["id"], area_2.id)
