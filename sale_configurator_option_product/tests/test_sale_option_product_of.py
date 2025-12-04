# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.sale_configurator_option.tests.common import Common


class TestProcess(Common):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        cls.product_opt_1.write({"type": "service"})
        cls.product_opt_2.write({"type": "consu"})

        cls.env.ref("stock.route_warehouse0_mto").active = True
        routes = [
            cls.env.ref("stock.route_warehouse0_mto").id,
            cls.env.ref("mrp.route_warehouse0_manufacture").id,
        ]
        cls.configurable_product = cls.env["product.product"].create(
            {
                "name": "Optional product",
                "type": "consu",
                "route_ids": [Command.set(routes)],
                "specific_option_ids": [
                    Command.create({"product_id": cls.product_opt_1.id}),
                    Command.create({"product_id": cls.product_opt_2.id}),
                ],
            }
        )
        cls.component = cls.env["product.product"].create(
            {"name": "Component", "type": "consu"}
        )
        cls.bom_configurable_product = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.configurable_product.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 1})
                ],
            }
        )

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.configurable_product.id,
                            "product_uom_qty": 2,
                            "child_option_ids": [
                                Command.create(
                                    {
                                        "product_id": cls.product_opt_1.id,
                                        "option_qty": 1,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                Command.create(
                                    {
                                        "product_id": cls.product_opt_2.id,
                                        "option_qty": 3,
                                        "option_qty_type": "proportional_qty",
                                    }
                                ),
                            ],
                        },
                    )
                ],
            }
        )

    def test_add_option_to_manufacture_order(self):
        self.sale_order.action_confirm()
        production = self.sale_order.mrp_production_ids

        self.assertNotIn(self.product_opt_1, production.move_raw_ids.product_id)
        self.assertIn(self.component, production.move_raw_ids.product_id)
        self.assertIn(self.product_opt_2, production.move_raw_ids.product_id)

        move_opt_2 = production.move_raw_ids.filtered(
            lambda m: m.product_id == self.product_opt_2
        )
        self.assertEqual(move_opt_2.product_uom_qty, 6)
