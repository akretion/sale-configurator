# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.pos_sale_order.tests.common import CommonCase


class TestCreateOrder(CommonCase):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.opt_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.opt_2 = cls.env.ref("sale_configurator_option.product_option_2")
        cls.opt_3 = cls.env.ref("sale_configurator_option.product_option_3")
        cls.product_with_option = cls.env.ref(
            "sale_configurator_option.product_with_option"
        )

        cls.lines = [
            (cls.product_with_option, 3.0),
            (cls.product1, 1.0),
            (cls.product2, 2.0),
        ]

    def _add_option(self, data):
        line = data["data"]["lines"][0][2]
        line["config"] = {
            "selected_options": [
                {
                    "price": 10,
                    "id": "1",
                    "product_id": self.opt_1.id,
                    "description": self.opt_1.name,
                    "notes": "My note",
                    "qty": 5,
                },
                {
                    "price": 20,
                    "id": "2",
                    "product_id": self.opt_2.id,
                    "description": self.opt_2.name,
                    "notes": "",
                    "qty": 3,
                },
                {
                    "price": 30,
                    "id": "3",
                    "product_id": self.opt_3.id,
                    "description": self.opt_3.name,
                    "notes": "",
                    "qty": 4,
                },
            ]
        }

    def test_create_sale(self):
        data = self._get_pos_data()
        self._add_option(data)
        sales = self._create_sale([data])
        self.assertEqual(len(sales), 1)
        sale = sales[0]
        self.assertEqual(len(sale.order_line), 6)
        # Note
        # we have 3 product with option the total price is
        # 3 * (5*10 + 3*20 + 4 * 30) = 690
        # For the two other normal product
        # 1*5 + 2*15 = 35
        # Except total : 725
        self.assertEqual(sale.amount_total, 725)
