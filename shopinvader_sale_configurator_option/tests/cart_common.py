# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CartCase


class ConfiguratorCartCommonCase(CartCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env.ref("sale_configurator_option.product_with_option")
        # test compatibility with search engine
        if hasattr(product.shopinvader_bind_ids, "recompute_json"):
            product.shopinvader_bind_ids.recompute_json()
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
