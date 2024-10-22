# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.tests.common import SavepointCase


class TestProcess(SavepointCase):
    @classmethod
    def setUpClassUsers(cls):
        super().setUpClassUsers()
        cls.shopfloor_user.groups_id += cls.env.ref("stock.group_stock_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=SUPERUSER_ID)  # CommonCase gives us a new user
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.env.ref("stock.route_warehouse0_mto").active = True
        cls.option_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.option_2 = cls.env.ref("sale_configurator_option.product_option_2")
        cls.option_3 = cls.env.ref("sale_configurator_option.product_option_3")
        (cls.option_1 + cls.option_2 + cls.option_3).write(
            {
                "type": "service",
            }
        )
        cls.product_with_option = cls.env["product.product"].create(
            {
                "name": "Optional product",
                "type": "product",
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("stock.route_warehouse0_mto").id,
                            cls.env.ref("mrp.route_warehouse0_manufacture").id,
                        ],
                    )
                ],
                "is_configurable_opt": True,
                "local_configurable_option_ids": [
                    (0, 0, {"product_id": cls.option_1.id}),
                    (0, 0, {"product_id": cls.option_2.id}),
                    (0, 0, {"product_id": cls.option_3.id}),
                ],
            }
        )
        cls.product_with_option_2 = cls.env["product.product"].create(
            {
                "name": "Optional product deux",
                "type": "product",
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            cls.env.ref("stock.route_warehouse0_mto").id,
                            cls.env.ref("mrp.route_warehouse0_manufacture").id,
                        ],
                    )
                ],
                "is_configurable_opt": True,
                "local_configurable_option_ids": [
                    (0, 0, {"product_id": cls.option_1.id}),
                    (0, 0, {"product_id": cls.option_2.id}),
                    (0, 0, {"product_id": cls.option_3.id}),
                ],
            }
        )
        cls.related_1 = cls.product_with_option.local_configurable_option_ids
        cls.related_2 = cls.product_with_option_2.local_configurable_option_ids

        cls.product_option = cls.env["product.product"].create(
            {
                "name": "product option consu",
                "type": "product",
            }
        )
        cls.bom_product_option = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_with_option.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_option.id,
                            "product_qty": 2,
                            "related_option_id": cls.related_1[1].id,
                        },
                    ),
                ],
            }
        )
        cls.bom_product_option_2 = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_with_option_2.product_tmpl_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_option.id,
                            "product_qty": 2,
                            "related_option_id": cls.related_2[2].id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_option.id,
                            "product_qty": 4,
                            "related_option_id": cls.related_2[1].id,
                        },
                    ),
                ],
            }
        )
        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_with_option.id,
                        "product_uom_qty": 2,
                        "option_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_1.id,
                                    "option_unit_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_2.id,
                                    "option_unit_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_3.id,
                                    "option_unit_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                        ],
                    },
                )
            ],
        }
        cls.sale_order = cls.env["sale.order"].create(vals)

        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_with_option.id,
                        "product_uom_qty": 2,
                        "option_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_1.id,
                                    "option_unit_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                        ],
                    },
                ),
            ],
        }
        cls.sale_order_2 = cls.env["sale.order"].create(vals)

        vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_with_option.id,
                        "product_uom_qty": 1,
                        "option_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_1.id,
                                    "option_unit_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_2.id,
                                    "option_unit_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_3.id,
                                    "option_unit_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                        ],
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": cls.product_with_option_2.id,
                        "product_uom_qty": 2,
                        "option_ids": [
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_1.id,
                                    "option_unit_qty": 2,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_2.id,
                                    "option_unit_qty": 3,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    "product_id": cls.option_3.id,
                                    "option_unit_qty": 1,
                                    "option_qty_type": "proportional_qty",
                                },
                            ),
                        ],
                    },
                ),
            ],
        }
        cls.sale_order_3 = cls.env["sale.order"].create(vals)

    def test_basic_process(self):
        self.sale_order.action_confirm()
        production = self.sale_order.production_ids.filtered(
            lambda m: m.product_id == self.product_with_option
        )
        self.assertTrue(production)
        line_option_1 = False
        line_product_2 = False
        for line in production.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
                self.assertEqual(line.product_uom_qty, 2)
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
                self.assertEqual(line.product_uom_qty, 8)
        self.assertFalse(line_option_1)
        self.assertTrue(line_product_2)

    def test_basic_process_2(self):
        self.sale_order_2.action_confirm()
        production = self.sale_order_2.production_ids.filtered(
            lambda m: m.product_id == self.product_with_option
        )
        self.assertTrue(production)
        line_option_1 = False
        line_product_2 = False
        for line in production.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
        self.assertFalse(line_option_1)
        self.assertFalse(line_product_2)

    def test_basic_process_3(self):
        self.sale_order_3.action_confirm()
        production = self.sale_order_3.production_ids.filtered(
            lambda m: m.product_id == self.product_with_option
        )
        production2 = self.sale_order_3.production_ids.filtered(
            lambda m: m.product_id == self.product_with_option_2
        )
        self.assertTrue(production)
        self.assertTrue(production2)
        line_option_1 = False
        line_product_2 = False
        line_option_3 = False
        for line in production.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
                self.assertEqual(line.product_uom_qty, 2)
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
                self.assertEqual(line.product_uom_qty, 2)
            if line.product_id.id == self.option_3.id:
                line_option_3 = True
        self.assertFalse(line_option_1)
        self.assertTrue(line_product_2)
        self.assertFalse(line_option_3)

        line_option_1 = False
        line_product_2 = False
        line_option_3 = False
        for line in production2.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
                self.assertEqual(line.product_uom_qty, 28)
            if line.product_id.id == self.option_3.id:
                line_option_3 = True
        self.assertFalse(line_option_1)
        self.assertTrue(line_product_2)
        self.assertFalse(line_option_3)