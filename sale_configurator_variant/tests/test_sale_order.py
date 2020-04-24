# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale = cls.env.ref("sale_configurator_variant.sale_order_1")
        cls.line_with_variant = cls.env.ref(
            "sale_configurator_variant.sale_order_line_1"
        )
        cls.line_variant_1 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_1"
        )
        cls.line_variant_2 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_2"
        )
        cls.line_variant_3 = cls.env.ref(
            "sale_configurator_variant.sale_order_line_variant_3"
        )
        cls.product_with_variant = cls.env.ref(
            "product.product_product_4_product_template"
        )
        cls.product_variant_1 = cls.env.ref("product.product_product_4")
        cls.product_variant_2 = cls.env.ref("product.product_product_4b")
        cls.product_variant_3 = cls.env.ref("product.product_product_4c")
        cls.product_variant_4 = cls.env.ref("product.product_product_4d")
        cls.product_variant_5 = cls.env.ref("sale.product_product_4e")
        cls.product_variant_6 = cls.env.ref("sale.product_product_4f")

    def create_sale_line_parent(self, product_tmpl):
        sale_line = self.env["sale.order.line"].create(
            {
                "name": product_tmpl.name,
                "product_tmpl_id": product_tmpl.id,
                "product_id": product_tmpl.product_variant_id.id,
                "product_tmpl_uom_qty": 1,
                "product_tmpl_uom": product_tmpl.uom_id.id,
                "price_unit": product_tmpl.list_price,
                "order_id": self.sale.id,
            }
        )
        return sale_line

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_total, 6850.80)
        self.assertEqual(self.sale.amount_untaxed, 6850.80)
        self.assertEqual(self.sale.amount_tax, 0)

    def test_conf_total_amount_price(self):
        self.assertEqual(self.line_with_variant.price_config_subtotal, 6850.80)
        self.assertEqual(self.line_with_variant.price_config_total, 6850.80)
        self.assertEqual(self.line_variant_1.price_config_total, 0)
        self.assertEqual(self.line_variant_2.price_config_total, 0)
        self.assertEqual(self.line_variant_3.price_config_total, 0)

    def test_conf_product_change_variant(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        new_line.product_tmpl_id_change()
        product_ids = set(new_line.variant_ids.mapped("product_id.id"))
        default_variants = {
                self.product_variant_1.id,
                self.product_variant_2.id,
                self.product_variant_3.id,
                self.product_variant_4.id,
                self.product_variant_5.id,
                self.product_variant_6.id,
        }
        self.assertEqual(product_ids, default_variants)

    def test_conf_product_variant_qty(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        new_line.product_tmpl_id_change()
        self.assertEqual(new_line.product_uom_qty, 6)
