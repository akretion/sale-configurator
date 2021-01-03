# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    child_type = fields.Selection(
        selection_add=[("option", "Option")],
        ondelete={"option": "set null"},
    )
    option_ids = fields.One2many(
        "sale.order.line",
        "parent_id",
        "Options",
        domain=[("child_type", "=", "option")],
        context={"default_child_type": "option"},
    )
    is_configurable_opt = fields.Boolean(
        "Is the product configurable Option ?", related="product_id.is_configurable_opt"
    )
    option_unit_qty = fields.Float(
        string="Option Unit Qty",
        digits="Product Unit of Measure",
        default=1.0,
    )
    option_qty_type = fields.Selection(
        [
            ("proportional_qty", "Proportional Qty"),
            ("independent_qty", "Independent Qty"),
        ],
        string="Option qty Type",
        compute="_compute_option_qty_type",
        store=True,
        readonly=False,
    )
    product_option_id = fields.Many2one(
        "product.configurator.option",
        "Product Option",
        ondelete="set null",
        compute="_compute_product_option_id",
    )
    product_uom_qty = fields.Float(
        compute="_compute_product_uom_qty",
        readonly=False,
        store=True,
    )

    def _get_child_type_sort(self):
        res = super()._get_child_type_sort()
        res.append((20, "option"))
        return res

    def _is_line_configurable(self):
        if self.is_configurable_opt:
            return True
        else:
            return super()._is_line_configurable()

    @api.depends(
        "product_uom_qty",
        "option_unit_qty",
        "option_qty_type",
        "parent_id.product_uom_qty",
    )
    def _compute_product_uom_qty(self):
        for record in self:
            if record.parent_id:
                if record.option_qty_type == "proportional_qty":
                    record.product_uom_qty = (
                        record.option_unit_qty * record.parent_id.product_uom_qty
                    )
                elif record.option_qty_type == "independent_qty":
                    record.product_uom_qty = record.option_unit_qty

    @api.onchange("product_uom_qty")
    def onchange_qty_propagate_to_child(self):
        # When adding a new configurable product the qty is not propagated
        # correctly to child line with the onchange (it work when modifying)
        # seem to have a bug in odoo ORM
        for record in self:
            record.option_ids._compute_product_uom_qty()

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        # For weird reason it seem that the product_uom_qty have been not recomputed
        # correctly. Recompute is only triggered in the onchange
        # and the onchange do not propagate the qty see the following test:
        # tests/test_sale_order.py::SaleOrderCase::test_create_sale_with_option_ids
        lines._compute_product_uom_qty()
        return lines

    @api.depends("product_id")
    def _compute_product_option_id(self):
        for record in self:
            record.product_option_id = (
                record.parent_id.product_id.configurable_option_ids.filtered(
                    lambda o: o.product_id == record.product_id
                )
            )

    @api.depends("product_id")
    def _compute_option_qty_type(self):
        for record in self:
            if record.product_option_id:
                record.option_qty_type = record.product_option_id.option_qty_type

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        self.option_ids = False
        if self.product_id.is_configurable_opt:
            for opt in self.product_id.configurable_option_ids:
                if opt.is_default_option:
                    option = self.new(
                        {
                            "product_id": opt.product_id.id,
                            "parent_id": self.id,
                            "child_type": "option",
                            "order_id": self.order_id.id,
                        }
                    )
                    option.product_id_change()
                    self.option_ids |= option
        return res
