# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_option_id = fields.Many2one(
        "sale.order.line", string="Parent Option", index=True
    )
    config_type = fields.Selection(
        selection_add=[("option", "Option")],
        ondelete={"option": "set null"},
    )
    child_option_ids = fields.One2many(
        "sale.order.line",
        "parent_option_id",
        "Options",
        copy=True,
    )
    option_qty = fields.Float(
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
        precompute=True,
        store=True,
        readonly=False,
    )
    option_id = fields.Many2one(
        "product.configurator.option",
        "Product Option",
        ondelete="set null",
        compute="_compute_option_id",
    )

    product_uom_qty = fields.Float(recursive=True)

    def _get_child_type_sort(self):
        res = super()._get_child_type_sort()
        res.append((20, "option"))
        return res

    def get_children(self):
        return super().get_children() + self.child_option_ids

    def _get_config_type(self):
        return self.product_id.config_type or super()._get_config_type()

    def _get_parent_id_from_vals(self, vals):
        if vals.get("parent_option_id"):
            return vals["parent_option_id"]
        else:
            return super()._get_parent_id_from_vals(vals)

    def _get_option(self):
        self.ensure_one()
        return self.parent_option_id.product_id.option_ids.filtered(
            lambda o: o.product_id == self.product_id
        )

    @api.depends("product_id")
    def _compute_option_id(self):
        for record in self:
            record.option_id = record._get_option()

    @api.depends("parent_option_id")
    def _compute_parent(self):  # pylint: disable=missing-return
        for record in self:
            if record.parent_option_id:
                record.parent_id = record.parent_option_id
                # record.config_type = "option"
            else:
                super(SaleOrderLine, record)._compute_parent()

    @api.depends(
        "product_uom_qty",
        "option_qty",
        "option_qty_type",
        "parent_option_id.product_uom_qty",
    )
    def _compute_product_uom_qty(self):  # pylint: disable=missing-return
        super()._compute_product_uom_qty()
        for record in self:
            if record.parent_option_id:
                if record.option_qty_type == "proportional_qty":
                    record.product_uom_qty = (
                        record.option_qty * record.parent_option_id.product_uom_qty
                    )
                elif record.option_qty_type == "independent_qty":
                    record.product_uom_qty = record.option_qty

    @api.depends("product_id")
    def _compute_option_qty_type(self):
        for record in self:
            if record.option_id:
                record.option_qty_type = record.option_id.option_qty_type

    @api.depends("child_option_ids")
    def _compute_report_line_is_empty_parent(self):  # pylint: disable=missing-return
        super()._compute_report_line_is_empty_parent()

    @api.depends("child_option_ids.price_subtotal", "child_option_ids.price_total")
    def _compute_config_amount(self):  # pylint: disable=missing-return
        super()._compute_config_amount()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        # We tried to avoid this onchange transforming child_option_ids in
        # a compute field, but it does not work in v18 because of too much confusions
        # between NewId and real records. Let's try again in next versions!
        res = super()._onchange_product_id()
        if self.product_id.config_type == "configurable":
            self.child_option_ids = False
            for opt in self.product_id.option_ids:
                if opt.is_default_option:
                    option = self.new(
                        {
                            "product_id": opt.product_id.id,
                            "parent_option_id": self.id,
                            "order_id": self.order_id.id,
                        }
                    )
                    option._onchange_product_id()
                    self.child_option_ids |= option
        return res

    @api.model_create_multi
    def create(self, vals_list):
        options_list = [vals.pop("child_option_ids", None) for vals in vals_list]
        lines = super().create(vals_list)
        # For weird reason it seem that the product_uom_qty have been not recomputed
        # correctly. Recompute is only triggered in the onchange
        # and the onchange do not propagate the qty see the following test:
        # test_sale_order.py::SaleOrderCase::test_create_sale_with_child_option_ids
        # Note maybe it's because the product_uom_qty have a default value
        # and so the create will add it, end then if we have a value the recompute
        # is note done
        lines._compute_product_uom_qty()

        # We ensure to write the option after all field on the main line are recomputed
        if any(options_list):
            for line, vals in zip(lines, options_list, strict=False):
                if vals:
                    line.write({"child_option_ids": vals})

        return lines
