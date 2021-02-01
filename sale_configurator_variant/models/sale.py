# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_variant_id = fields.Many2one(
        "sale.order.line", "Parent Variant", ondelete="cascade", index=True
    )
    variant_ids = fields.One2many("sale.order.line", "parent_variant_id", "Variants")
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        domain=[("sale_ok", "=", True)],
        change_default=True,
        ondelete="restrict",
    )
    is_variant_qty_need_recompute = fields.Boolean(
        compute="_compute_is_variant_qty_need_recompute", store=True
    )
    parent_variant_qty = fields.Float(
        related="parent_variant_id.product_uom_qty", readonly=False
    )
    is_multi_variant_line = fields.Boolean(
        "Multi variant",
    )

    def _get_child_type_sort(self):
        res = super()._get_child_type_sort()
        res.append((10, "variant"))
        return res

    def _is_line_configurable(self):
        if self.parent_variant_id:
            return False
        elif self.is_multi_variant_line:
            return True
        else:
            return super()._is_line_configurable()

    @api.depends("variant_ids.product_uom_qty", "product_uom_qty")
    def _compute_is_variant_qty_need_recompute(self):
        for variant_line in self:
            if variant_line.parent_variant_id:
                variant_line = variant_line.parent_variant_id
            records = variant_line.filtered("variant_ids")

            for record in records:
                qty = variant_line._get_child_qty()
                record.is_variant_qty_need_recompute = qty != record.product_uom_qty

    def _get_child_qty(self):
        self.ensure_one()
        return sum(self.variant_ids.mapped("product_uom_qty"))

    def _set_parent_variant_qty(self):
        """
        This method is in charge of compute qty of parent variant
        sale order line
        """
        records = self.filtered("is_variant_qty_need_recompute")
        for record in records:
            if record.variant_ids:
                record.product_uom_qty = record._get_child_qty()
        return records

    def _recompute_done(self, field):
        super()._recompute_done(field)
        if field.name == "is_variant_qty_need_recompute":
            with_variant_qty = self.exists()._set_parent_variant_qty()
            with_variant_qty.write({"is_variant_qty_need_recompute": False})

    def _prepare_sale_line_variant(self, variant):
        return {
            "order_id": self.order_id.id,
            "product_id": variant.id,
            "product_uom_qty": 1,
            "product_uom": variant.uom_id,
            "name": self.get_sale_order_line_multiline_description_sale(variant),
        }

    @api.onchange("product_tmpl_id")
    def product_tmpl_id_change(self):
        self.variant_ids = False
        if self.product_tmpl_id:
            # ToFIX set product_id to False raise error on[
            #  _sql_constraints = accountable_required_fields
            self.product_id = self.product_tmpl_id.product_variant_id
        return {}

    def _get_sale_line_price_variant(self, variant):
        price_unit = self.env["account.tax"]._fix_tax_included_price_company(
            self._get_display_price(variant),
            variant.taxes_id,
            self.tax_id,
            self.company_id,
        )
        return price_unit

    @api.onchange("variant_ids")
    def variant_id_change(self):
        res = {}
        for opt in self.variant_ids:
            self._set_parent_variant_qty()
            ctx = opt.env.context.copy()
            ctx.update({"quantity": self.product_uom_qty})
            variant = opt.product_id.with_context(ctx)
            opt.price_unit = self._get_sale_line_price_variant(variant)
        return res

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        order_id = self.env.context.get("order_id")
        if not self.order_id and order_id:
            self.order_id = order_id
        if self.product_tmpl_id:
            self.name = self.product_tmpl_id.name
        return res
