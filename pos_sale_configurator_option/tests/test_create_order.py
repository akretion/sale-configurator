# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.pos_sale_order.tests.common import CommonCase


class TestCreateOrder(CommonCase):
    @classmethod
    def _get_pos_line(cls):
        cls.line_opt_1 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_1"
        )
        cls.line_opt_2 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_2"
        )
        cls.line_opt_3 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_3"
        )
        cls.product_with_option = cls.env.ref(
            "sale_configurator_option.product_with_option"
        )

        res, amount = super()._get_pos_line()
        res.append(
            [
                0,
                0,
                {
                    "price_unit": 180,
                    "product_id": cls.product_with_option.id,
                    "tax_ids": [[6, 0, []]],
                    "qty": 2,
                    "config": {
                        "selected_options": [
                            {
                                "price": 10,
                                "id": "1",
                                "product_id": cls.line_opt_1.id,
                                "description": cls.line_opt_1.name,
                                "notes": "My note",
                                "quantity": 5,
                            },
                            {
                                "price": 20,
                                "id": "2",
                                "product_id": cls.line_opt_2.id,
                                "description": cls.line_opt_2.name,
                                "notes": "",
                                "quantity": 3,
                            },
                            {
                                "price": 5,
                                "id": "3",
                                "product_id": cls.line_opt_3.id,
                                "description": cls.line_opt_3.name,
                                "notes": "",
                                "quantity": 4,
                            },
                        ]
                    },
                },
            ]
        )
        amount += 360
        return res, amount

    def test_create_sale(self):
        data = self._get_pos_data()
        sales = self._create_sale([data])
        self.assertEqual(len(sales), 1)
        sale = sales[0]
        self.assertEqual(len(sale.order_line), 7)
        # TODO finish test
