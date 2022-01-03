from odoo.addons.shopinvader.tests.test_cart import CartCase


class ConfiguratorCartCase(CartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_with_option_message = cls.env.ref(
            "sale_configurator_option_message.product_with_option_message"
        )
        # test compatibility with search engine
        if hasattr(
            cls.product_with_option_message.shopinvader_bind_ids, "recompute_json"
        ):
            cls.product_with_option_message.shopinvader_bind_ids.recompute_json()
        cls.option_message = cls.env.ref(
            "sale_configurator_option_message.product_configurator_option_with_message"
        )

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.shopinvader_session = {}
        self.partner = self.backend.anonymous_partner_id
        with self.work_on_services(
            partner=None, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_add_item_with_option_message(self):
        res = self.service.dispatch(
            "add_item",
            params={
                "item_qty": 1,
                "product_id": self.product_with_option_message.id,
                "options": [
                    {
                        "option_id": self.option_message.id,
                        "qty": 1,
                        "message": "The Message",
                    },
                ],
            },
        )
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0]["option"]["product"]["name"], "Option with message")
        self.assertEqual(options[0]["message"], "The Message")

    def test_add_item_without_option(self):
        res = self.service.dispatch(
            "add_item",
            params={
                "item_qty": 1,
                "product_id": self.product_with_option_message.id,
            },
        )
        self.assertEqual(len(res["data"]["lines"]["items"]), 1)
        options = res["data"]["lines"]["items"][0]["options"]
        self.assertEqual(len(options), 0)
