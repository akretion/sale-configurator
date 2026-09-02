# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.sale_configurator_option.tests.common import Common


class TestProcess(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        (cls.product_opt_1 + cls.product_opt_2 + cls.product_opt_3).write(
            {"type": "service"}
        )
        cls.env.ref("stock.route_warehouse0_mto").active = True
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
        cls.conf_product_options = cls.configurable_product.specific_option_ids
        cls.conf_product_2_options = cls.configurable_product_2.specific_option_ids

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
                            "related_option_id": cls.conf_product_options[1].id,
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
                            "product_qty": 4,
                            # Related to "Option 2"
                            "related_option_id": cls.conf_product_2_options[1].id,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": cls.component.id,
                            "product_qty": 2,
                            # Related to "Option 3"
                            "related_option_id": cls.conf_product_2_options[2].id,
                        },
                    ),
                ],
            }
        )
        cls.sale_order = cls.env["sale.order"].create({"partner_id": cls.partner.id})

    def _create_sale_line(self, product_id, quantity, vals_child_option_ids):
        self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": product_id.id,
                "product_uom_qty": quantity,
                "child_option_ids": vals_child_option_ids,
            }
        )

    def test_component_related_to_the_option_sold(self):
        vals_child_option_ids = [
            Command.create(
                {
                    "product_id": self.product_opt_1.id,
                    "option_qty": 1,
                    "option_qty_type": "proportional_qty",
                },
            ),
            Command.create(
                {
                    "product_id": self.product_opt_2.id,
                    "option_qty": 3,
                    "option_qty_type": "independent_qty",
                },
            ),
        ]
        self._create_sale_line(self.configurable_product, 4, vals_child_option_ids)
        self.sale_order.action_confirm()
        production = self.sale_order.mrp_production_ids
        self.assertNotIn(self.product_opt_1, production.move_raw_ids.product_id)
        self.assertIn(self.component, production.move_raw_ids.product_id)

        move_component = production.move_raw_ids
        # BoM: 2 components related to "Option 2" for each Configurable Product
        # Sale Order: 3 "Option 2" sold
        # Expected Component quantity to manufacture = 2 * 3
        self.assertEqual(move_component.product_uom_qty, 6)

    def test_component_not_related_to_the_option_sold(self):
        vals_child_option_ids = [
            Command.create(
                {
                    "product_id": self.product_opt_1.id,
                    "option_qty": 1,
                    "option_qty_type": "proportional_qty",
                },
            ),
        ]
        self._create_sale_line(self.configurable_product, 2, vals_child_option_ids)
        self.sale_order.action_confirm()
        production = self.sale_order.mrp_production_ids

        # The component of Configurable Product is related to "Option 2"
        # In sale_order we sell only the "Option 1"
        # => The Manufacture Order created for Configurable Product is empty
        self.assertFalse(production.move_raw_ids)

    def test_component_related_to_2_options_sold_in_2_lines(self):
        vals_child_option_ids_1 = [
            Command.create(
                {
                    "product_id": self.product_opt_2.id,
                    "option_qty": 1,
                    "option_qty_type": "independent_qty",
                },
            ),
        ]
        self._create_sale_line(self.configurable_product, 1, vals_child_option_ids_1)

        vals_child_option_ids_2 = [
            Command.create(
                {
                    "product_id": self.product_opt_2.id,
                    "option_qty": 3,
                    "option_qty_type": "independent_qty",
                },
            ),
            Command.create(
                {
                    "product_id": self.product_opt_3.id,
                    "option_qty": 1,
                    "option_qty_type": "independent_qty",
                },
            ),
        ]
        self._create_sale_line(self.configurable_product_2, 2, vals_child_option_ids_2)

        self.sale_order.action_confirm()

        production_ids = self.sale_order.mrp_production_ids
        self.assertNotIn(self.product_opt_2, production_ids.move_raw_ids.product_id)
        self.assertNotIn(self.product_opt_3, production_ids.move_raw_ids.product_id)

        production = production_ids.filtered(
            lambda m: m.product_id == self.configurable_product
        )
        production2 = production_ids.filtered(
            lambda m: m.product_id == self.configurable_product_2
        )

        move_component_1 = production.move_raw_ids
        self.assertEqual(self.component, move_component_1.product_id)
        # BoM: 2 components related to "Option 2" for each Configurable Product
        # Sale Order Line n°1: 1 "Option 2" sold
        # Expected Component quantity to manufacture = 2 * 1
        self.assertEqual(move_component_1.product_uom_qty, 2)

        move_component_2 = production2.move_raw_ids
        self.assertEqual(self.component, move_component_2.product_id)
        # BoM for each Configurable Product n°2:
        #     - 4 components related to "Option 2"
        #     - 2 components related to "Option 3"
        # Sale Order Line n°2:
        #     - 3 "Option 2" sold
        #     - 1 "Option 3" sold
        # Expected component quantity to manufacture:
        #     - one line of 4 * 3 components
        #     - one line of 2 * 1 components
        self.assertEqual(move_component_2.mapped("product_uom_qty"), [12, 2])
