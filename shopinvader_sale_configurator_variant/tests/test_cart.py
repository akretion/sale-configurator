# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_sale_configurator_option.tests.cart_common import (
    ConfiguratorCartCommonCase,
)


class ConfiguratorCartCase(ConfiguratorCartCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.variant_1 = cls.env.ref("product.product_product_4")
        cls.variant_2 = cls.env.ref("product.product_product_4b")
        cls.variant_3 = cls.env.ref("product.product_product_4c")
        cls.item_params = {
            "variants": [
                {"product_id": cls.variant_1.id, "qty": 10},
                {"product_id": cls.variant_2.id, "qty": 15},
                {"product_id": cls.variant_3.id, "qty": 20},
            ]
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

    def test_add_multi_variant_item(self):
        res = self.service.dispatch("add_multi_variant_item", params=self.item_params)
        items = res["data"]["lines"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["qty"], 45)
        self.assertEqual(items[0]["amount"]["price"], 0)
        variants = items[0]["variants"]
        self.assertEqual(len(variants), 3)

    def test_update_multi_variant_item(self):
        res = self.service.dispatch("add_multi_variant_item", params=self.item_params)
        self.shopinvader_session["cart_id"] = res["data"]["id"]
        item = res["data"]["lines"]["items"][0]
        res = self.service.dispatch(
            "update_multi_variant_item",
            params={
                "item_id": item["id"],
                "variants": [{"product_id": self.variant_1.id, "qty": 12}],
            },
        )
        items = res["data"]["lines"]["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["qty"], 12)
        variants = items[0]["variants"]
        self.assertEqual(len(variants), 1)
