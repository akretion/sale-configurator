# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def sync_sequence(self):
        for record in self:
            count = 0
            for line in record.order_line.sorted("sequence"):
                if not line.parent_option_id:
                    line.sequence = count
                    count += 1
                    for option in line.option_ids:
                        option.sequence = count
                        count += 1

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.sync_sequence()
        return records

    def write(self, vals):
        super().write(vals)
        if "order_line" in vals:
            self.sync_sequence()
        return True

    @api.onchange("order_line")
    def onchange_sale_line_sequence(self):
        self.sync_sequence()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_option_id = fields.Many2one(
        "sale.order.line", "Parent Option", ondelete="cascade", index=True
    )
    option_ids = fields.One2many("sale.order.line", "parent_option_id", "Options")
    is_configurable_opt = fields.Boolean(
        "Is the product configurable Option ?", related="product_id.is_configurable_opt"
    )
    option_unit_qty = fields.Float(
        string="Option Unit Qty",
        digits=dp.get_precision("Product Unit of Measure"),
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

    def _is_line_configurable(self):
        if self.is_configurable_opt:
            return True
        else:
            return super()._is_line_configurable()

    @api.depends(
        "product_uom_qty", "option_unit_qty", "parent_option_id.product_uom_qty"
    )
    def _compute_product_uom_qty(self):
        for record in self:
            if record.parent_option_id:
                if record.option_qty_type == "proportional_qty":
                    record.product_uom_qty = (
                        record.option_unit_qty * record.parent_option_id.product_uom_qty
                    )
                elif record.option_qty_type == "independent_qty":
                    record.product_uom_qty = record.option_unit_qty

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("parent_option_id") and "order_id" not in vals:
                vals["order_id"] = self.browse(vals["parent_option_id"]).order_id.id
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

    @api.depends(
        "option_ids.price_subtotal", "option_ids.price_total", "parent_option_id"
    )
    def _compute_config_amount(self):
        super()._compute_config_amount()

    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super()._get_price_config_subtotal()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            for opt in self.option_ids:
                res += opt.price_subtotal
        return res

    @api.model
    def _get_price_config_total(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super()._get_price_config_total()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            for opt in self.option_ids:
                res += opt.price_total
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
        if self.product_id.is_option and self.parent_option_id:
            product_tmpl_id = self.parent_option_id.product_id.product_tmpl_id
            option_ids = product_tmpl_id.configurable_option_ids.filtered(
                lambda o: o.product_id == self.product_id
            )
            option_id = option_ids and option_ids[0] or False
            self.product_option_id = option_id
            self.update(self.parent_option_id._prepare_sale_line_option(option_id))
        return res
