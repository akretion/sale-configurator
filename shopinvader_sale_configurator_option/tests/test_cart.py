# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .cart_common import ConfiguratorCartCommonCase


class ConfiguratorCartCase(ConfiguratorCartCommonCase):
    def test_add_item_with_option(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 2)
        self.assertEqual(options[0]["option"]["product"]["name"], "Option 1")
        self.assertEqual(options[1]["option"]["product"]["name"], "Option 2")

    def test_add_two_item_with_option(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.shopinvader_session["cart_id"] = res["data"]["id"]
        res = self.service.dispatch("add_item", params=self.item_params)
        self.assertEqual(len(res["data"]["lines"]["items"]), 2)

    def test_update_item_with_option(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.shopinvader_session["cart_id"] = res["data"]["id"]
        item_id = res["data"]["lines"]["items"][0]["id"]
        res = self.service.dispatch(
            "update_item", params={"item_id": item_id, "item_qty": 5}
        )
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        self.assertEqual(res["data"]["lines"]["items"][0]["qty"], 5)

    def test_update_option_action_replace(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.shopinvader_session["cart_id"] = res["data"]["id"]
        item_id = res["data"]["lines"]["items"][0]["id"]
        opt3 = self.env.ref("sale_configurator_option.product_configurator_option_2")
        res = self.service.dispatch(
            "update_item",
            params={
                "item_id": item_id,
                "item_qty": 1,
                "options": [{"option_id": opt3.id, "qty": 3}],
            },
        )
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0]["qty"], 3)
