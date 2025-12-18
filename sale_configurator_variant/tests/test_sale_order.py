# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class SaleConfiguratorVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Product with Variants
        # ----------------------
        Template = cls.env["product.template"]
        Attribute = cls.env["product.attribute"]
        AttributeValue = cls.env["product.attribute.value"]
        SaleOrderLine = cls.env["sale.order.line"]

        cls.attr_ref = Attribute.create(
            {"name": "Attribute Ref", "create_variant": "always"}
        )
        cls.value_ids = AttributeValue.create(
            [{"name": f"V {i}", "attribute_id": cls.attr_ref.id} for i in range(1, 6)]
        )

        cls.product_with_variant = Template.create(
            {
                "name": "Test Configurable Product",
                "description_sale": "Description",
                "list_price": 750,
                "taxes_id": [Command.set([])],
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attr_ref.id,
                            "value_ids": [Command.set(cls.value_ids.ids)],
                        },
                    ),
                ],
            }
        )
        cls.variants = cls.product_with_variant.product_variant_ids.sorted(
            lambda r: r.product_template_attribute_value_ids.name[1:]
        )
        cls.product_variant_1 = cls.variants[0]
        cls.product_variant_2 = cls.variants[1]
        cls.product_variant_3 = cls.variants[2]
        cls.product_variant_4 = cls.variants[3]
        cls.product_variant_5 = cls.variants[4]

        cls.product_variant_2.description_sale = "Description"
        cls.product_variant_3.product_template_attribute_value_ids.price_extra = 50

        # Sale Order
        # ----------
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Pricelist", "sequence": 1}
        )
        cls.sale = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "pricelist_id": cls.pricelist.id}
        )

        cls.line_with_variant = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "product_template_id": cls.product_with_variant.id,
                "product_id": cls.product_variant_1.id,
                "is_configurable_with_variant": True,
            }
        )
        cls.line_variant_1 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_variant_id": cls.line_with_variant.id,
                "product_id": cls.product_variant_1.id,
                "product_uom_qty": 4,
            }
        )

        cls.line_variant_2 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_variant_id": cls.line_with_variant.id,
                "product_id": cls.product_variant_2.id,
                "product_uom_qty": 3,
            }
        )

        cls.line_variant_3 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_variant_id": cls.line_with_variant.id,
                "product_id": cls.product_variant_3.id,
                "product_uom_qty": 2,
            }
        )

    def _conf_product_add_variants(self, sale_line):
        default_variants = [
            self.product_variant_1,
            self.product_variant_2,
            self.product_variant_3,
            self.product_variant_4,
            self.product_variant_5,
        ]
        for prod in default_variants:
            vrt_vals = {
                "order_id": sale_line.order_id.id,
                "product_id": prod.id,
                "product_uom": prod.uom_id.id,
                "product_uom_qty": 1,
                "parent_variant_id": sale_line.id,
                "price_unit": prod.list_price,
            }
            sale_line.create(vrt_vals)

    def create_sale_line_parent(self, product_tmpl):
        sale_line = self.env["sale.order.line"].create(
            {
                "name": product_tmpl.name,
                "product_template_id": product_tmpl.id,
                "product_id": product_tmpl.product_variant_id.id,
                "price_unit": product_tmpl.list_price,
                "order_id": self.sale.id,
                "is_configurable_with_variant": True,
            }
        )
        return sale_line

    def test_onchange_product_template_id(self):
        with Form(
            self.env["sale.order.line"].with_context(default_order_id=self.sale.id)
        ) as line_form:
            line_form.is_configurable_with_variant = True
            line_form.product_template_id = self.product_with_variant
            self.assertEqual(line_form.product_id, self.product_variant_1)

    def test_quantity_readonly(self):
        with Form(
            self.env["sale.order.line"].with_context(default_order_id=self.sale.id)
        ) as line_form:
            line_form.is_configurable_with_variant = True
            line_form.product_template_id = self.product_with_variant
            with line_form.variant_ids.new() as variant:
                variant.product_id = self.product_variant_4
            with self.assertRaisesRegex(AssertionError, "can't write on readonly"):
                line_form.product_uom_qty = 3

    def test_config_type(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        self._conf_product_add_variants(new_line)
        for line in new_line.variant_ids:
            self.assertEqual(line.config_type, "variant")
        self.assertEqual(new_line.config_type, "configurable")

    def test_parent_variant_name(self):
        self.assertEqual(
            self.sale.order_line[0].name, "Test Configurable Product\nDescription"
        )
        self.assertEqual(
            self.sale.order_line[1].name, "Test Configurable Product (V 1)"
        )
        self.assertEqual(
            self.sale.order_line[2].name, "Test Configurable Product (V 2)"
        )

    def test_total_amount(self):
        self.assertEqual(self.sale.amount_tax, 0)
        self.assertEqual(self.sale.amount_total, 6850)
        self.assertEqual(self.sale.amount_untaxed, 6850)

    def test_update_price(self):
        self.sale._recompute_prices()
        self.assertEqual(self.sale.amount_total, 6850)
        self.assertEqual(self.sale.amount_untaxed, 6850)
        self.assertEqual(self.sale.amount_tax, 0)

    def test_price_config_total(self):
        self.assertEqual(self.line_with_variant.price_config_subtotal, 6850)
        self.assertEqual(self.line_with_variant.price_config_total, 6850)
        self.assertEqual(self.line_variant_1.price_config_total, 0)
        self.assertEqual(self.line_variant_2.price_config_total, 0)
        self.assertEqual(self.line_variant_3.price_config_total, 0)

    def test_parent_quantity(self):
        new_line = self.create_sale_line_parent(self.product_with_variant)
        self._conf_product_add_variants(new_line)
        self.assertEqual(new_line.product_uom_qty, 5)
        new_line.variant_ids[0].product_uom_qty = 3
        self.assertEqual(new_line.product_uom_qty, 7)

    def test_variant_price_depends_on_global_qty(self):
        self.assertEqual(self.line_variant_1.price_unit, 750)

        self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "applied_on": "1_product",
                "product_tmpl_id": self.product_with_variant.id,
                "compute_price": "percentage",
                "percent_price": 20,
                "min_quantity": 10,
            }
        )
        self.line_variant_2.product_uom_qty = 4

        self.assertEqual(self.line_variant_1.price_unit, 600)
        self.assertEqual(self.line_variant_2.price_unit, 600)
        self.assertEqual(self.line_variant_3.price_unit, 640)

    def test_variant_price_depends_on_global_qty_and_local_pricelist(self):
        self.env["product.pricelist.item"].create(
            [
                {
                    "pricelist_id": self.pricelist.id,
                    "applied_on": "1_product",
                    "product_tmpl_id": self.product_with_variant.id,
                    "compute_price": "percentage",
                    "percent_price": 20,
                    "min_quantity": 10,
                },
                {
                    "pricelist_id": self.pricelist.id,
                    "applied_on": "0_product_variant",
                    "product_id": self.product_variant_2.id,
                    "compute_price": "percentage",
                    "percent_price": 50,
                    "min_quantity": 10,
                },
            ]
        )
        self.line_variant_3.product_uom_qty = 3

        self.assertEqual(self.line_variant_1.price_unit, 600)
        self.assertEqual(self.line_variant_2.price_unit, 375)
        self.assertEqual(self.line_variant_3.price_unit, 640)
