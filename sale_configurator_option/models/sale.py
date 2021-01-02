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
    )
    product_option_id = fields.Many2one(
        "product.configurator.option",
        "Product Option",
        ondelete="set null",
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

    @api.depends("product_uom_qty", "option_unit_qty", "parent_id.product_uom_qty")
    def _compute_product_uom_qty(self):
        for record in self:
            if record.parent_id:
                if record.option_qty_type == "proportional_qty":
                    record.product_uom_qty = (
                        record.option_unit_qty * record.parent_id.product_uom_qty
                    )
                elif record.option_qty_type == "independent_qty":
                    record.product_uom_qty = record.option_unit_qty

    @api.model_create_multi
    def create(self, vals_list):
        # TODO CHECK
        lines = super().create(vals_list)
        # For weird reason it seem that the product_uom_qty have been not recomputed
        # correctly. Recompute is only triggered in the onchange
        # and the onchange do not propagate the qty
        lines._compute_product_uom_qty()
        return lines

    @api.onchange("product_option_id")
    def product_option_id_change(self):
        res = {}
        self.product_id = self.product_option_id.product_id
        return res

    def _prepare_sale_line_option(self, opt):
        if opt:
            proportional_qty = 1.0
            if opt.option_qty_type == "proportional_qty":
                proportional_qty = 1.0 * self.product_uom_qty
            return {
                "order_id": self.order_id.id,
                "product_id": opt.product_id.id,
                "option_unit_qty": 1.0,
                "product_uom_qty": proportional_qty,
                "product_uom": opt.product_uom_id.id,
                "option_qty_type": opt.option_qty_type,
                "product_option_id": opt.id,
            }
        else:
            return {
                "order_id": self.order_id.id,
            }

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        self.option_ids = False
        if self.product_id.is_configurable_opt:
            options = []
            for opt in self.product_id.configurable_option_ids:
                if opt.is_default_option:
                    options.append((0, 0, self._prepare_sale_line_option(opt)))
            self.option_ids = options
        if self.product_id.is_option and self.parent_id:
            product_tmpl_id = self.parent_id.product_id.product_tmpl_id
            option_ids = product_tmpl_id.configurable_option_ids.filtered(
                lambda o: o.product_id == self.product_id
            )
            option_id = option_ids and option_ids[0] or False
            self.product_option_id = option_id
            self.update(self.parent_id._prepare_sale_line_option(option_id))
        return res
