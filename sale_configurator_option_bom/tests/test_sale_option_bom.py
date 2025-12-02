# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, Command

from odoo.addons.sale_configurator_option.tests.common import Common


class TestProcess(Common):
    @classmethod
    def setUpClassUsers(cls):  # pylint: disable=missing-return
        super().setUpClassUsers()
        cls.shopfloor_user.groups_id += cls.env.ref("stock.group_stock_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=SUPERUSER_ID)  # CommonCase gives us a new user
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.env.ref("stock.route_warehouse0_mto").active = True
        (cls.product_opt_1 + cls.product_opt_2 + cls.product_opt_3).write(
            {"type": "service"}
        )
        routes = [
            cls.env.ref("stock.route_warehouse0_mto").id,
            cls.env.ref("mrp.route_warehouse0_manufacture").id,
        ]
        cls.configurable_product = cls.env["product.product"].create(
            {
                "name": "Configurable Product 1",
                "type": "consu",
                "route_ids": [Command.set(routes)],
                "config_type": "configurable",
                "specific_option_ids": [
                    Command.create({"product_id": cls.product_opt_1.id}),
                    Command.create({"product_id": cls.product_opt_2.id}),
                    Command.create({"product_id": cls.product_opt_3.id}),
                ],
            }
        )
        cls.configurable_product_2 = cls.env["product.product"].create(
            {
                "name": "Configurable Product 2",
                "type": "consu",
                "route_ids": [Command.set(routes)],
                "config_type": "configurable",
                "specific_option_ids": [
                    Command.create({"product_id": cls.product_opt_1.id}),
                    Command.create({"product_id": cls.product_opt_2.id}),
                    Command.create({"product_id": cls.product_opt_3.id}),
                ],
            }
        )
        cls.related_1 = cls.configurable_product.specific_option_ids
        cls.related_2 = cls.configurable_product_2.specific_option_ids

        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu"}
        )
        cls.bom_configurable_product = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.configurable_product.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 2,
                            # Related to Option 2
                            "related_option_id": cls.related_1[1].id,
                        },
                    ),
                ],
            }
        )
        cls.bom_configurable_product_2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.configurable_product_2.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 2,
                            # Related to "Option 3"
                            "related_option_id": cls.related_2[2].id,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 4,
                            # Related to "Option 2"
                            "related_option_id": cls.related_2[1].id,
                        },
                    ),
                ],
            }
        )

        sol_option_1 = Command.create(
            {
                "product_id": cls.product_opt_1.id,
                "option_qty": 1,
                "option_qty_type": "proportional_qty",
            },
        )
        sol_option_2 = Command.create(
            {
                "product_id": cls.product_opt_2.id,
                "option_qty": 2,
                "option_qty_type": "proportional_qty",
            },
        )
        sol_option_3 = Command.create(
            {
                "product_id": cls.product_opt_3.id,
                "option_qty": 2,
                "option_qty_type": "proportional_qty",
            },
        )

        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": cls.configurable_product.id,
                        "product_uom_qty": 2,
                        "child_option_ids": [sol_option_1, sol_option_2, sol_option_3],
                    },
                )
            ],
        }
        cls.sale_order = cls.env["sale.order"].create(vals)

        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": cls.configurable_product.id,
                        "product_uom_qty": 2,
                        "child_option_ids": [sol_option_1],
                    },
                ),
            ],
        }
        cls.sale_order_2 = cls.env["sale.order"].create(vals)

        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                Command.create(
                    {
                        "product_id": cls.configurable_product.id,
                        "product_uom_qty": 1,
                        "child_option_ids": [
                            Command.create(
                                {
                                    "product_id": cls.product_opt_1.id,
                                    "option_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            Command.create(
                                {
                                    "product_id": cls.product_opt_2.id,
                                    "option_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            sol_option_3,
                        ],
                    },
                ),
                Command.create(
                    {
                        "product_id": cls.configurable_product_2.id,
                        "product_uom_qty": 2,
                        "child_option_ids": [
                            Command.create(
                                {
                                    "product_id": cls.product_opt_1.id,
                                    "option_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            Command.create(
                                {
                                    "product_id": cls.product_opt_2.id,
                                    "option_qty": 3,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            Command.create(
                                {
                                    "product_id": cls.product_opt_3.id,
                                    "option_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                        ],
                    },
                ),
            ],
        }
        cls.sale_order_3 = cls.env["sale.order"].create(vals)

    def test_component_related_to_the_option_sold(self):
        self.sale_order.action_confirm()
        production = self.sale_order.mrp_production_ids
        self.assertNotIn(self.product_opt_1, production.move_raw_ids.product_id)
        self.assertIn(self.component, production.move_raw_ids.product_id)

        move_component = production.move_raw_ids
        # BoM: 2 components related to "Option 2" for each Configurable Product
        # Sale Order: 2 Configurable Product sold => 2 * 2 "Option 2" sold
        # Expected Component quantity to manufacture = 2 * 4
        self.assertEqual(move_component.product_uom_qty, 8)

    def test_component_not_related_to_the_option_sold(self):
        self.sale_order_2.action_confirm()
        production = self.sale_order_2.mrp_production_ids.filtered(
            lambda m: m.product_id == self.configurable_product
        )
        # The component of Configurable Product is related to "Option 2"
        # In sale_order_2 we sell only the "Option 1"
        # => The Manufacture Order created for Configurable Product is empty
        self.assertFalse(production.move_raw_ids)

    def test_component_related_to_2_options_sold_twice(self):
        self.sale_order_3.action_confirm()
        production = self.sale_order_3.mrp_production_ids.filtered(
            lambda m: m.product_id == self.configurable_product
        )
        production2 = self.sale_order_3.mrp_production_ids.filtered(
            lambda m: m.product_id == self.configurable_product_2
        )

        self.assertNotIn(self.product_opt_1, production.move_raw_ids.product_id)
        self.assertNotIn(self.product_opt_3, production.move_raw_ids.product_id)
        self.assertIn(self.component, production.move_raw_ids.product_id)

        move_component = production.move_raw_ids
        # BoM: 2 components related to "Option 2" for each Configurable Product
        # Sale Order: 1 Configurable Product sold => 1 * 1 "Option 2" sold
        # Expected Component quantity to manufacture = 2 * 1
        self.assertEqual(move_component.product_uom_qty, 2)

        self.assertNotIn(self.product_opt_1, production2.move_raw_ids.product_id)
        self.assertNotIn(self.product_opt_3, production2.move_raw_ids.product_id)
        self.assertIn(self.component, production2.move_raw_ids.product_id)

        move_component = production2.move_raw_ids
        # BoM for each Configurable Product n°2:
        #     - 4 components related to "Option 2"
        #     - 2 components related to "Option 3"
        # Sale Order: 2 Configurable Product sold =>
        #     - 2 * 3 "Option 2" sold
        #     - 2 * 1 "Option 3" sold
        # Expected component quantity to manufacture = 4 * 6 + 2 * 2
        self.assertEqual(move_component.product_uom_qty, 28)
