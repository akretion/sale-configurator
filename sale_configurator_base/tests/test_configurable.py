# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestConfigurable(SavepointCase):
    def setUp(self):
        super().setUp()
        example_product = self.env.ref("product.product_product_4")
        example_product.invoice_policy = "order"
        self.sale_order = self.env["sale.order"].create(
            {"partner_id": self.env.ref("base.res_partner_10").id}
        )
        example_line_vals = {
            "order_id": self.sale_order.id,
            "product_id": example_product.id,
            "product_uom_qty": 1,
            "price_unit": 22,
        }
        lines = self.env["sale.order.line"]
        for _ in range(4):
            lines += self.env["sale.order.line"].create(example_line_vals)
        lines[2:4].write({"parent_id": lines[1]})

    def test_create_invoice(self):
        """
        Test we get the same parent-child relationships
        when creating an invoice from a sale order
        """
        self.sale_order.action_confirm()
        invoice_lines = self.sale_order._create_invoices().line_ids
        self.assertFalse(invoice_lines[0].parent_id)
        self.assertFalse(invoice_lines[0].child_ids)
        self.assertEqual(invoice_lines[2:4].mapped("parent_id"), invoice_lines[1])
