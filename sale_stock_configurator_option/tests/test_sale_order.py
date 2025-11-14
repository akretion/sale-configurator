# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import TransactionCase


class SaleOrderCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_option.sale_order_1")
        cls.sale.order_line._compute_qty_delivered_method()

    def test_qty_delivered_method(self):
        for line in self.sale.order_line.filtered(
            lambda line: line.child_type == "option"
        ):
            self.assertEqual(line.qty_delivered_method, "option_proportional")

    def test_validation(self):
        self.sale.action_confirm()
        self.assertEqual(len(self.sale.picking_ids.move_ids), 1)

    def test_picking_validation_full(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        picking.button_validate()

        for line in self.sale.order_line:
            self.assertEqual(line.qty_delivered, line.product_uom_qty)

    def test_picking_validation_half(self):
        self.sale.action_confirm()
        picking = self.sale.picking_ids
        picking.move_ids.quantity = 0.5
        picking.with_context(skip_backorder=True).button_validate()

        for line in self.sale.order_line:
            self.assertEqual(line.qty_delivered, line.product_uom_qty / 2)
