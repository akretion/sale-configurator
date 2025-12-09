# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.sale_configurator_option.tests.common import Common


class TestOptionWithVariant(Common):
    @classmethod
    def _add_pricelist_item(cls, product, price_unit):
        return cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.id,
                "compute_price": "fixed",
                "fixed_price": price_unit,
                "min_quantity": 40,
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env["product.product"]
        ConfigOption = cls.env["product.configurator.option"]

        # Products
        # --------

        cls.attr_ref = cls.env["product.attribute"].create(
            {"name": "Attribute Ref", "create_variant": "always"}
        )
        cls.value_ids = cls.env["product.attribute.value"].create(
            [{"name": f"V {i}", "attribute_id": cls.attr_ref.id} for i in range(1, 3)]
        )

        cls.product_with_var_opt = cls.env["product.template"].create(
            {
                "name": "Configurable Product with Variants",
                "list_price": 750,
                "taxes_id": [Command.set([])],
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attr_ref.id,
                            "value_ids": [Command.set(cls.value_ids.ids)],
                        },
                    ),
                ],
            }
        )

        cls.variant_1, cls.variant_2 = cls.product_with_var_opt.product_variant_ids
        cls.variant_1.name = "Variant 1"

        cls.product_opt_1 = Product.create(
            {"name": "Option 1", "list_price": 150, "config_type": "option"}
        )
        cls.product_opt_2 = Product.create(
            {"name": "Option 2", "list_price": 250, "config_type": "option"}
        )

        # Configurator Options
        # -------------------
        ConfigOption.create(
            [
                {
                    "configurable_product_tmpl_id": cls.product_with_var_opt.id,
                    "product_id": cls.product_opt_1.id,
                    "is_default_option": True,
                    "option_qty_type": "proportional_qty",
                    "sequence": 1,
                },
                {
                    "configurable_product_tmpl_id": cls.product_with_var_opt.id,
                    "product_id": cls.product_opt_2.id,
                    "is_default_option": True,
                    "option_qty_type": "independent_qty",
                    "sequence": 2,
                },
            ]
        )

        # Add price per qty for variant
        cls.product_with_var_opt.list_price = 50
        cls.pricelist_item = cls._add_pricelist_item(cls.product_with_var_opt, 30)

        # Add price per qty for option
        cls._add_pricelist_item(cls.product_opt_1.product_tmpl_id, 130)
        cls._add_pricelist_item(cls.product_opt_2.product_tmpl_id, 230)

        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "pricelist_id": cls.pricelist.id,
                "order_line": [
                    Command.create(
                        {
                            "is_multi_variant_line": True,
                            "product_template_id": cls.product_with_var_opt.id,
                            # TODO: comment le remplir automatiquement sans onchange?
                            "product_id": cls.variant_1.id,
                            "name": "Test",
                            "variant_ids": [
                                Command.create(
                                    {
                                        "product_uom_qty": 30,
                                        "product_id": cls.variant_1.id,
                                    },
                                ),
                                Command.create(
                                    {
                                        "product_uom_qty": 20,
                                        "product_id": cls.variant_2.id,
                                    },
                                ),
                            ],
                            "child_option_ids": [
                                Command.create(
                                    {
                                        "option_qty": 1,
                                        "product_id": cls.product_opt_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                Command.create(
                                    {
                                        "option_qty": 2,
                                        "product_id": cls.product_opt_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )

    def test_create_sale_with_option_and_variant(self):
        lines = self.sale.order_line.sorted("sequence")

        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0].product_uom_qty, 50)
        self.assertEqual(lines[0].config_type, "configurable")
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

    def test_duplicate_sale(self):
        ori_sale = self.sale
        sale = ori_sale.copy()
        lines = sale.order_line.sorted("sequence")

        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0].product_uom_qty, 50)
        self.assertEqual(lines[0].config_type, "configurable")
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
