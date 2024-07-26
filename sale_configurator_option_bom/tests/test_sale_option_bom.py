# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID

from odoo.addons.mindef_sale.tests.common import MindefSaleCase
from odoo.addons.shopfloor.tests.common import CommonCase


class TestProcess(CommonCase, MindefSaleCase):
    @classmethod
    def setUpClassUsers(cls):
        super().setUpClassUsers()
        cls.shopfloor_user.groups_id += cls.env.ref("stock.group_stock_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(user=SUPERUSER_ID)  # CommonCase gives us a new user
        cls.env["exception.rule"].search([]).write({"active": False})
        cls.env.ref("stock.route_warehouse0_mto").active = True
        cls.option_1 = cls.env.ref("sale_configurator_option.product_option_1")
        cls.option_2 = cls.env.ref("sale_configurator_option.product_option_2")
        cls.option_3 = cls.env.ref("sale_configurator_option.product_option_3")
        (cls.option_1 + cls.option_2 + cls.option_3).write(
            {
                "type": "service",
                "available_in_pos": True,
            }
        )
        cls.product_with_option = cls.env["product.product"].create(
            {
                "name": "Optional product",
                "type": "product",
                "is_repaired": False,
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
                # "tracking": "lot",
                "auto_generate_prodlot": True,
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
                "is_repaired": False,
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
                # "tracking": "lot",
                "auto_generate_prodlot": True,
                "is_configurable_opt": True,
                "local_configurable_option_ids": [
                    (0, 0, {"product_id": cls.option_1.id}),
                    (0, 0, {"product_id": cls.option_2.id}),
                    (0, 0, {"product_id": cls.option_3.id}),
                ],
            }
        )
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
                            "related_option": cls.option_2.id,
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
                            "related_option": cls.option_3.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_option.id,
                            "product_qty": 4,
                            "related_option": cls.option_2.id,
                        },
                    ),
                ],
            }
        )
        cls.sale_order = cls._create_mindef_so(
            [
                (
                    cls.product_with_option.id,
                    2,
                    [
                        (cls.option_1.id, 1),
                        (cls.option_2.id, 2),
                        (cls.option_3.id, 2),
                    ],
                ),
            ]
        )
        cls.sale_order_2 = cls._create_mindef_so(
            [
                (
                    cls.product_with_option.id,
                    1,
                    [
                        (cls.option_1.id, 1),
                    ],
                ),
            ]
        )
        cls.sale_order_3 = cls._create_mindef_so(
            [
                (
                    cls.product_with_option.id,
                    1,
                    [
                        (cls.option_1.id, 2),
                        (cls.option_2.id, 1),
                        (cls.option_3.id, 2),
                    ],
                ),
                (
                    cls.product_with_option_2.id,
                    2,
                    [
                        (cls.option_1.id, 2),
                        (cls.option_2.id, 3),
                        (cls.option_3.id, 1),
                    ],
                ),
            ]
        )

    def test_basic_process(self):
        List_Manuf_order_1 = self.env["mrp.production"].search([])
        indice_start = len(List_Manuf_order_1)
        self.assertEqual(indice_start, 4)
        self.assertTrue(self.sale_order.action_confirm())
        List_Manuf_order = self.env["mrp.production"].search([])
        product_ok = False
        indice = 0
        for Manuf_order in List_Manuf_order:
            indice = indice + 1
            if Manuf_order.product_id.id == self.product_with_option.id:
                product_ok = True
                Manuf_order_trouver = Manuf_order
        self.assertEqual(indice, 5)
        self.assertTrue(product_ok)
        line_option_1 = False
        line_product_2 = False
        for line in Manuf_order_trouver.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
                self.assertEqual(line.product_uom_qty, 2)
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
                self.assertEqual(line.product_uom_qty, 8)
        self.assertFalse(line_option_1)
        self.assertTrue(line_product_2)

    def test_basic_process_2(self):
        self.assertTrue(self.sale_order_2.action_confirm())
        List_Manuf_order = self.env["mrp.production"].search([])
        product_ok = False
        for Manuf_order in List_Manuf_order:
            if Manuf_order.product_id.id == self.product_with_option.id:
                product_ok = True
                Manuf_order_trouver = Manuf_order
        self.assertTrue(product_ok)
        line_option_1 = False
        line_product_2 = False
        for line in Manuf_order_trouver.move_raw_ids:
            if line.product_id.id == self.option_1.id:
                line_option_1 = True
            if line.product_id.id == self.product_option.id:
                line_product_2 = True
        self.assertFalse(line_option_1)
        self.assertFalse(line_product_2)

    def test_basic_process_3(self):
        indic_list_of = self.env["mrp.production"].search([])
        self.assertEqual(len(indic_list_of), 4)
        self.assertTrue(self.sale_order_3.action_confirm())
        List_Manuf_order = self.env["mrp.production"].search([])
        self.assertEqual(len(List_Manuf_order), 6)
        product_ok = False
        product_ok2 = False
        for Manuf_order in List_Manuf_order:
            if Manuf_order.product_id.id == self.product_with_option.id:
                product_ok = True
                Manuf_order_trouver = Manuf_order
            if Manuf_order.product_id.id == self.product_with_option_2.id:
                product_ok2 = True
                Manuf_order_trouver2 = Manuf_order
        self.assertTrue(product_ok)
        self.assertTrue(product_ok2)
        line_option_1 = False
        line_product_2 = False
        line_option_3 = False
        for line in Manuf_order_trouver.move_raw_ids:
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
        for line in Manuf_order_trouver2.move_raw_ids:
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
