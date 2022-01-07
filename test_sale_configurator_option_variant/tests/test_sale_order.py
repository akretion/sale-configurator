# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def _add_pricelist_item(cls, product, price_unit):
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": price_unit,
                "min_quantity": 40,
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_with_option = cls.env.ref(
            "sale_configurator_option.product_with_option"
        )
        cls.product_with_option.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.env.ref(
                                "product.product_attribute_1"
                            ).id,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    [
                                        cls.env.ref(
                                            "product.product_attribute_value_1"
                                        ).id,
                                        cls.env.ref(
                                            "product.product_attribute_value_2"
                                        ).id,
                                    ],
                                )
                            ],
                        },
                    )
                ]
            }
        )
        cls.product_option_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.product_option_2 = cls.env.ref("sale_configurator_option.product_option_2")
        cls.variant_1, cls.variant_2 = cls.product_with_option.product_variant_ids
        cls.pricelist = cls.env.ref("product.list0")

        # Add price per qty for variant
        cls.product_with_option.list_price = 50
        cls._add_pricelist_item(cls.product_with_option, 30)

        # Add price per qty for option
        cls.product_option_1.list_price = 150
        cls._add_pricelist_item(cls.product_option_1, 130)
        cls.product_option_2.list_price = 250
        cls._add_pricelist_item(cls.product_option_2, 230)

    def test_create_sale_with_option_and_variant(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "pricelist_id": self.pricelist.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "is_multi_variant_line": True,
                            "product_id": self.product_with_option.id,
                            "product_tmpl_id": self.product_with_option.product_tmpl_id.id,
                            "option_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "option_unit_qty": 1,
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
                            "variant_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "product_uom_qty": 30,
                                        "product_id": self.variant_1.id,
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "product_uom_qty": 20,
                                        "product_id": self.variant_2.id,
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        lines = sale.order_line
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0].product_uom_qty, 50)
        self.assertTrue(lines[0].is_configurable)
        self.assertEqual(lines[0].price_unit, 0)

        self.assertEqual(lines[1].product_uom_qty, 30)
        self.assertEqual(lines[1].price_unit, 30)

        self.assertEqual(lines[2].product_uom_qty, 20)
        self.assertEqual(lines[2].price_unit, 30)

        self.assertEqual(lines[3].product_uom_qty, 50)
        self.assertEqual(lines[3].price_unit, 130)

        self.assertEqual(lines[4].product_uom_qty, 100)
        self.assertEqual(lines[4].price_unit, 230)

        self.assertEqual(lines[0].price_config_subtotal, 31000)
