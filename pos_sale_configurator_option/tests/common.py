# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.pos_sale_order.tests.common import CommonCase


class CommonOptionCase(CommonCase):
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
                    "note": "My note",
                    "qty": 5,
                },
                {
                    "price": 20,
                    "id": "2",
                    "product_id": self.opt_2.id,
                    "description": self.opt_2.name,
                    "note": "",
                    "qty": 3,
                },
                {
                    "price": 30,
                    "id": "3",
                    "product_id": self.opt_3.id,
                    "description": self.opt_3.name,
                    "note": "",
                    "qty": 4,
                },
            ]
        }
