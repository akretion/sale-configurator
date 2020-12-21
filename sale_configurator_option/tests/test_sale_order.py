# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_option.sale_order_1")
        cls.line_with_opt = cls.env.ref("sale_configurator_option.sale_order_line_1")
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
        cls.product_option_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.product_option_2 = cls.env.ref("sale_configurator_option.product_option_2")

    def create_sale_line(self, product):
        sale_line = self.env["sale.order.line"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 1,
                "product_uom": product.uom_id.id,
                "price_unit": product.list_price,
                "order_id": self.sale.id,
            }
        )
        return sale_line

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_total, 126.50)
        self.assertEqual(self.sale.amount_untaxed, 110)
        self.assertEqual(self.sale.amount_tax, 16.5)
        self.assertEqual(self.line_with_opt.price_config_subtotal, 110)
        self.assertEqual(self.line_with_opt.price_config_total, 126.50)

    def test_change_price_unit_option(self):
        self.line_opt_1.price_unit = 40
        self.assertEqual(self.line_opt_1.price_subtotal, 80)
        self.assertEqual(self.line_with_opt.price_config_subtotal, 170)

    def test_change_price_unit_main(self):
        self.line_with_opt.price_unit = 100
        self.assertEqual(self.line_with_opt.price_config_subtotal, 210)
        self.assertEqual(self.line_with_opt.price_config_total, 241.5)

    def test_change_option_qty(self):
        self.line_opt_1.option_unit_qty = 10
        self.assertEqual(self.line_opt_1.product_uom_qty, 10)
        self.assertEqual(self.line_opt_1.price_subtotal, 100)
        self.assertEqual(self.line_with_opt.price_config_subtotal, 190)

    def test_change_main_qty(self):
        self.line_with_opt.product_uom_qty = 2
        self.assertEqual(self.line_opt_1.product_uom_qty, 4)
        self.assertEqual(self.line_opt_1.price_subtotal, 40)
        self.assertEqual(self.line_with_opt.price_config_subtotal, 220)

    def test_conf_product_change_option(self):
        new_line = self.create_sale_line(self.product_with_option)
        new_line.product_id_change()
        product_ids = set(new_line.option_ids.mapped("product_id.id"))
        default_options = {self.product_option_1.id, self.product_option_2.id}
        self.assertEqual(product_ids, default_options)

    def test_create_sale_with_option_ids(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_with_option.id,
                            "product_uom_qty": 2,
                            "option_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "option_unit_qty": 5,
                                        "product_id": self.product_option_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "option_unit_qty": 2,
                                        "product_id": self.product_option_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        lines = sale.order_line
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].product_uom_qty, 2)
        self.assertTrue(lines[0].is_configurable)
        self.assertEqual(lines[1].product_uom_qty, 10)
        self.assertEqual(lines[1].price_subtotal, 100)

        self.assertEqual(lines[2].product_uom_qty, 4)
        self.assertEqual(lines[2].price_subtotal, 80)

        self.assertEqual(lines[0].price_config_subtotal, 180)

    def test_order_line_order_create(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "sequence": 10,
                            "product_id": self.product_with_option.id,
                            "product_uom_qty": 2,
                            "option_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "sequence": 1,
                                        "option_unit_qty": 5,
                                        "product_id": self.product_option_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "sequence": 20,
                                        "option_unit_qty": 2,
                                        "product_id": self.product_option_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        sale.refresh()
        lines = sale.order_line
        self.assertEqual(lines[0].sequence, 0)
        self.assertFalse(lines[0].parent_option_id)
        self.assertEqual(lines[1].sequence, 1)
        self.assertTrue(lines[1].parent_option_id)
        self.assertEqual(lines[2].sequence, 2)
        self.assertTrue(lines[1].parent_option_id)
