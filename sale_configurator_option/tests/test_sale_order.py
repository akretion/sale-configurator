# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from .common import Common


class SaleConfiguratorOption(Common):
    def _add_pricelist_item(self, product, qty, price_unit):
        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": product.product_tmpl_id.id,
                "compute_price": "fixed",
                "fixed_price": price_unit,
                "min_quantity": qty,
            }
        )

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product_with_opt.id,
                            "product_uom_qty": 2,
                            "child_option_ids": [
                                Command.create(
                                    {
                                        "option_qty": 5,
                                        "product_id": self.product_opt_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                Command.create(
                                    {
                                        "option_qty": 2,
                                        "product_id": self.product_opt_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )

    def _create_sale_line(self, product):
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

    def test_sale_option_readonly(self):
        form = Form(self.sale)

        for i in [0, 1, 2, 3]:
            with form.order_line.edit(i) as line_form:
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.product_id = self.product_normal
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.product_uom_qty = 4
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.price_unit = 4
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.price_subtotal = 4

    def test_sale_product_editable(self):
        form = Form(self.sale)
        with form.order_line.new() as new_line:
            new_line.product_id = self.product_normal
            new_line.product_uom_qty = 4
            new_line.price_unit = 4
            with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                new_line.price_subtotal = 4

    def test_invoice_option_readonly(self):
        self.sale.action_confirm()
        invoice = self.sale._create_invoices()
        form = Form(invoice)

        for i in [1, 2, 3]:
            with form.invoice_line_ids.edit(i) as line_form:
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.product_id = self.product_normal
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.quantity = 4
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.price_unit = 4
                with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                    line_form.price_subtotal = 4

    def test_invoice_product_editable(self):
        self.sale.action_confirm()
        invoice = self.sale._create_invoices()
        form = Form(invoice)

        with form.invoice_line_ids.new() as new_line:
            new_line.product_id = self.product_normal
            new_line.quantity = 4
            new_line.price_unit = 4
            with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                new_line.price_subtotal = 4

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_total, 126.50)
        self.assertEqual(self.sale.amount_untaxed, 110)
        self.assertEqual(self.sale.amount_tax, 16.5)
        self.assertEqual(self.line_product_with_opt.price_config_subtotal, 110)
        self.assertEqual(self.line_product_with_opt.price_config_total, 126.50)

    def test_change_price_unit_option(self):
        self.line_opt_1.price_unit = 40
        self.assertEqual(self.line_opt_1.price_subtotal, 80)
        self.assertEqual(self.line_product_with_opt.price_config_subtotal, 170)

    def test_change_price_unit_main(self):
        self.line_product_with_opt.price_unit = 100
        self.assertEqual(self.line_product_with_opt.price_config_subtotal, 210)
        self.assertEqual(self.line_product_with_opt.price_config_total, 241.5)

    def test_change_option_qty(self):
        self.line_opt_1.option_qty = 10
        self.assertEqual(self.line_opt_1.product_uom_qty, 10)
        self.assertEqual(self.line_opt_1.price_subtotal, 100)
        self.assertEqual(self.line_product_with_opt.price_config_subtotal, 190)

    def test_change_main_qty(self):
        self.line_product_with_opt.product_uom_qty = 2
        self.assertEqual(self.line_opt_1.product_uom_qty, 4)
        self.assertEqual(self.line_opt_1.price_subtotal, 40)
        self.assertEqual(self.line_product_with_opt.price_config_subtotal, 220)

    def test_change_main_qty_with_pricelist(self):
        self._add_pricelist_item(self.product_opt_1, 4, 5)
        self.line_product_with_opt.product_uom_qty = 2
        self.assertEqual(self.line_opt_1.price_unit, 5)

    def test_conf_product_change_option(self):
        self.env = self.env(context={"add_default_option": True})
        new_line = self._create_sale_line(self.product_with_opt)
        new_line._onchange_product_id()
        product_ids = set(new_line.child_option_ids.mapped("product_id.id"))
        default_options = {self.product_opt_1.id, self.product_opt_2.id}
        self.assertEqual(product_ids, default_options)

    def test_create_sale_with_child_option_ids(self):
        sale = self._create_sale_order()
        lines = sale.order_line
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0].product_uom_qty, 2)
        self.assertEqual(lines[0].config_type, "configurable")
        self.assertEqual(lines[1].product_uom_qty, 10)
        self.assertEqual(lines[1].price_subtotal, 100)

        self.assertEqual(lines[2].product_uom_qty, 4)
        self.assertEqual(lines[2].price_subtotal, 80)

        self.assertEqual(lines[0].price_config_subtotal, 180)

    def test_create_sale_with_pricelist(self):
        self._add_pricelist_item(self.product_opt_1, 10, 5)
        self._add_pricelist_item(self.product_opt_2, 4, 10)

        sale = self._create_sale_order()
        lines = sale.order_line
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[1].price_unit, 5)
        self.assertEqual(lines[2].price_unit, 10)

    def test_create_line_before_save(self):
        line = self.env["sale.order.line"].create(
            {"order_id": self.sale.id, "name": "test"}
        )

        form = Form(line)
        form.product_id = self.product_with_opt
        self.assertEqual(form.config_type, "configurable")
        self.assertEqual(len(form.child_option_ids), 2)

    def test_order_line_order_create_check_sequence(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "sequence": 10,
                            "product_id": self.product_with_opt.id,
                            "product_uom_qty": 2,
                            "child_option_ids": [
                                Command.create(
                                    {
                                        "sequence": 30,
                                        "option_qty": 5,
                                        "product_id": self.product_opt_1.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                                Command.create(
                                    {
                                        "sequence": 20,
                                        "option_qty": 2,
                                        "product_id": self.product_opt_2.id,
                                        "option_qty_type": "proportional_qty",
                                    },
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        sale.invalidate_recordset()
        lines = sale.order_line
        self.assertEqual(lines[0].sequence, 0)
        self.assertFalse(lines[0].parent_id)
        self.assertEqual(lines[1].sequence, 1)
        self.assertTrue(lines[1].parent_id)
        self.assertEqual(lines[1].product_id, self.product_opt_2)
        self.assertEqual(lines[2].sequence, 2)
        self.assertTrue(lines[1].parent_id)
        self.assertEqual(lines[2].product_id, self.product_opt_1)

    def test_order_line_write_check_sequence(self):
        sale = self._create_sale_order()
        line_normal = self.env["sale.order.line"].create(
            {"product_id": self.product_normal.id, "order_id": sale.id}
        )
        line_configurable = sale.order_line.filtered(
            lambda x: x.product_id == self.product_with_opt
        )
        # Inital sequences
        self.assertEqual(line_configurable.sequence, 0)
        self.assertEqual(line_normal.sequence, 10)

        # Mimicking the sequence widget's Drag and Drop
        sale.write(
            {"order_line": [Command.update(line_configurable.id, {"sequence": 2})]}
        )
        # New sequences
        self.assertEqual(line_configurable.sequence, 0)
        self.assertEqual(line_normal.sequence, 3)

        sale.write(
            {"order_line": [Command.update(line_configurable.id, {"sequence": 20})]}
        )
        self.assertEqual(line_configurable.sequence, 1)
        self.assertEqual(line_normal.sequence, 0)

    def test_copy_sale(self):
        sale = self._create_sale_order()
        self.assertEqual(len(sale.order_line), 3)
        self.assertEqual(len(sale.main_line_ids), 1)
        main_line = sale.main_line_ids
        options = sale.order_line - main_line
        self.assertEqual(len(options), 2)
        self.assertEqual(options[0].parent_id, main_line)
        self.assertEqual(options[1].parent_id, main_line)
        self.assertEqual(options[0].parent_option_id, main_line)
        self.assertEqual(options[1].parent_option_id, main_line)
        self.assertEqual(options, main_line.child_option_ids)

        sale_copy = sale.copy()
        self.assertEqual(len(sale_copy.order_line), 3)
        self.assertEqual(len(sale_copy.main_line_ids), 1)
        main_line_copy = sale_copy.main_line_ids
        options_copy = sale_copy.order_line - main_line_copy
        self.assertEqual(len(options_copy), 2)
        self.assertEqual(options_copy[0].parent_id, main_line_copy)
        self.assertEqual(options_copy[1].parent_id, main_line_copy)
        self.assertEqual(options_copy[0].parent_option_id, main_line_copy)
        self.assertEqual(options_copy[1].parent_option_id, main_line_copy)
        self.assertEqual(options_copy, main_line_copy.child_option_ids)

        self.assertNotEqual(main_line, main_line_copy)
        self.assertNotEqual(options[0], options_copy[0])
        self.assertNotEqual(options[1], options_copy[1])

    def test_hide_subtotal(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_normal.id, "product_uom_qty": 2},
                    )
                ],
            }
        )
        self.assertTrue(sale.order_line.hide_subtotal)
        self.assertTrue(sale.hide_subtotal)
