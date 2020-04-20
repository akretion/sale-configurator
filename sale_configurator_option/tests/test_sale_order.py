# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_option.sale_order_1")
        cls.line_with_opt = cls.env.ref(
            "sale_configurator_option.sale_order_line_1")
        cls.line_opt_1 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_1")
        cls.line_opt_2 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_2")
        cls.line_opt_3 = cls.env.ref(
            "sale_configurator_option.sale_order_line_option_3")

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_total, 126.50)
        self.assertEqual(self.sale.amount_untaxed, 110)
        self.assertEqual(self.sale.amount_tax, 16.5)

    def test_conf_total_amount_main_without_price(self):
        self.assertEqual(self.line_with_opt.price_config_subtotal, 110)
        self.assertEqual(self.line_with_opt.price_config_total, 126.5)
        self.assertEqual(self.line_opt_1.price_config_total, 0)
        self.assertEqual(self.line_opt_2.price_config_total, 0)
        self.assertEqual(self.line_opt_3.price_config_total, 0)

    def test_conf_total_amount_main_without_price(self):
        # Set price to product with option and check totals
        self.line_with_opt.price_unit = 100
        self.assertEqual(self.line_with_opt.price_config_subtotal, 210)
        self.assertEqual(self.line_with_opt.price_config_total, 241.5)
        self.assertEqual(self.line_opt_1.price_config_total, 0)
        self.assertEqual(self.line_opt_2.price_config_total, 0)
        self.assertEqual(self.line_opt_3.price_config_total, 0)
