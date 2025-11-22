# Copyright 2025 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Product = cls.env["product.product"]
        ConfigOption = cls.env["product.configurator.option"]
        SaleOrderLine = cls.env["sale.order.line"]

        # Products
        # --------
        cls.product_with_opt = Product.create(
            {
                "name": "Product With Option",
                "config_type": "configurable",
                "list_price": 0,
            }
        )
        cls.product_with_opt_tmpl = cls.product_with_opt.product_tmpl_id

        cls.product_opt_1 = Product.create(
            {"name": "Option 1", "lst_price": 10, "config_type": "option"}
        )
        cls.product_opt_2 = Product.create(
            {"name": "Option 2", "lst_price": 20, "config_type": "option"}
        )
        cls.product_opt_3 = Product.create(
            {"name": "Option 3", "lst_price": 30, "config_type": "option"}
        )
        cls.product_normal = Product.create({"name": "Product"})

        # Options Configurators
        # -------------------
        cls.config_opt_1 = ConfigOption.create(
            {
                "configurable_product_tmpl_id": cls.product_with_opt_tmpl.id,
                "product_id": cls.product_opt_1.id,
                "is_default_option": True,
                "option_qty_type": "proportional_qty",
                "sequence": 1,
            }
        )
        cls.config_opt_2 = ConfigOption.create(
            {
                "configurable_product_tmpl_id": cls.product_with_opt_tmpl.id,
                "product_id": cls.product_opt_2.id,
                "is_default_option": True,
                "option_qty_type": "independent_qty",
                "sequence": 2,
            }
        )
        cls.config_opt_3 = ConfigOption.create(
            {
                "configurable_product_tmpl_id": cls.product_with_opt_tmpl.id,
                "product_id": cls.product_opt_3.id,
                "option_qty_type": "proportional_qty",
                "sequence": 3,
            }
        )

        # Sale Order
        # ----------
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Pricelist", "sequence": 1}
        )

        cls.sale = cls.env["sale.order"].create(
            {"partner_id": cls.partner.id, "pricelist_id": cls.pricelist.id}
        )

        cls.line_product_with_opt = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "product_id": cls.product_with_opt.id,
            }
        )
        cls.line_opt_1 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_option_id": cls.line_product_with_opt.id,
                "product_id": cls.product_opt_1.id,
                "option_qty": 2,
                "option_qty_type": "proportional_qty",
            }
        )

        cls.line_opt_2 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_option_id": cls.line_product_with_opt.id,
                "product_id": cls.product_opt_2.id,
                "option_qty": 3,
                "option_qty_type": "proportional_qty",
            }
        )

        cls.line_opt_3 = SaleOrderLine.create(
            {
                "order_id": cls.sale.id,
                "parent_option_id": cls.line_product_with_opt.id,
                "product_id": cls.product_opt_3.id,
                "option_qty": 1,
                "option_qty_type": "proportional_qty",
            }
        )
