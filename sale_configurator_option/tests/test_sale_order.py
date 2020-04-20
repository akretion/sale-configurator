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
        cls.product_option_1 = cls.env.ref(
            "sale_configurator_option.product_with_option_2")
        cls.product_with_option_2 = cls.env.ref(
            "sale_configurator_option.product_with_option_2")
        cls.line_with_opt_2 = cls.env['sale.order.line'].create({
            'name': cls.product_option_1.name,
            'product_id': cls.product_option_1.id,
            'product_uom_qty': 2,
            'product_uom': cls.product_option_1.uom_id.id,
            'price_unit': cls.product_option_1.list_price,
            'order_id': cls.sale.id,
        })

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

    def test_conf_product_change_option(self):
        self.line_with_opt_2.product_id = self.product_with_option_2
        self.line_with_opt_2.product_id_change()
        default_options = [
            x.product_id
            for x in self.product_with_option_2.product_tmpl_id.
            product_config_opt_ids
            if x.opt_default_qty > 0]
        self.assertEqual(len(self.line_with_opt_2.option_ids), len(default_options))

    def test_conf_product_default_opt_qty(self):
        qties = {
            x.product_id: x.opt_default_qty
            for x in self.product_with_option_2.product_tmpl_id.
            product_config_opt_ids}
        for opt in self.line_with_opt_2.option_ids:
            self.assertEqual(
                opt.product_uom_qty, qties[opt.product_id],
                "Option qty error on product %s" % opt.product_id.name)
