# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader.tests.test_cart import CartCase


class ConfiguratorCartCase(CartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env.ref("sale_configurator_option.product_with_option")
        opt1 = cls.env.ref("sale_configurator_option.product_configurator_option_1")
        opt2 = cls.env.ref("sale_configurator_option.product_configurator_option_2")
        cls.item_params = {
            "item_qty": 1,
            "product_id": product.id,
            "options": [
                {"option_id": opt1.id, "qty": 2},
                {"option_id": opt2.id, "qty": 2},
            ],
        }

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.shopinvader_session = {}
        self.partner = self.backend.anonymous_partner_id
        self.product_1 = self.env.ref("product.product_product_4b")
        self.sale_obj = self.env["sale.order"]
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_add_item_with_option(self):
        res = self.service.dispatch("add_item", params=self.item_params)
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 2)

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
