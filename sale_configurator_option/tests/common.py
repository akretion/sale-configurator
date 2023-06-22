# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class SaleOrderCommon(SavepointCase):
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

    @classmethod
    def create_sale_line(cls, product):
        sale_line = cls.env["sale.order.line"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 1,
                "product_uom": product.uom_id.id,
                "price_unit": product.list_price,
                "order_id": cls.sale.id,
            }
        )
        return sale_line
