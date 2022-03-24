# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase

# /!\ /!\ Be carefull when running test /!\ /!\
# As Odoo post process the installation of accounting
# you must first install sale module (so the pricelist will be in dollars)
# then you install the sale_configurator_option module so the data are in dollars
# if not you will have inconsistency order in EUR with pricelist in dollars


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_option.sale_order_1")
        cls.pricelist = cls.env.ref("product.list0")
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

    @classmethod
    def _add_pricelist_item(cls, product, qty, price_unit):
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": price_unit,
                "min_quantity": qty,
            }
        )

    @classmethod
    def _create_sale_order(cls):
        return cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
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
                                        "option_unit_qty": 5,
                                        "product_id": cls.product_option_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "option_unit_qty": 2,
                                        "product_id": cls.product_option_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )

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

    def test_change_main_qty_with_pricelist(self):
        self._add_pricelist_item(self.product_option_1, 4, 5)
        self.line_with_opt.product_uom_qty = 2
        self.assertEqual(self.line_opt_1.price_unit, 5)

    def test_conf_product_change_option(self):
        self.env = self.env(context={"add_default_option": True})
        new_line = self.create_sale_line(self.product_with_option)
        new_line.product_id_change()
        product_ids = set(new_line.option_ids.mapped("product_id.id"))
        default_options = {self.product_option_1.id, self.product_option_2.id}
        self.assertEqual(product_ids, default_options)

    def test_create_sale_with_option_ids(self):
        sale = self._create_sale_order()
        lines = sale.order_line
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].product_uom_qty, 2)
        self.assertTrue(lines[0].is_configurable)
        self.assertEqual(lines[1].product_uom_qty, 10)
        self.assertEqual(lines[1].price_subtotal, 100)

        self.assertEqual(lines[2].product_uom_qty, 4)
        self.assertEqual(lines[2].price_subtotal, 80)

        self.assertEqual(lines[0].price_config_subtotal, 180)

    def test_create_sale_with_pricelist(self):
        self._add_pricelist_item(self.product_option_1, 10, 5)
        self._add_pricelist_item(self.product_option_2, 4, 10)

        sale = self._create_sale_order()
        lines = sale.order_line
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[1].price_unit, 5)
        self.assertEqual(lines[2].price_unit, 10)

    def test_order_line_order_create_check_sequence(self):
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
                                        "sequence": 30,
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
        self.assertFalse(lines[0].parent_id)
        self.assertEqual(lines[1].sequence, 1)
        self.assertTrue(lines[1].parent_id)
        self.assertEqual(lines[1].product_id, self.product_option_2)
        self.assertEqual(lines[2].sequence, 2)
        self.assertTrue(lines[1].parent_id)
        self.assertEqual(lines[2].product_id, self.product_option_1)
