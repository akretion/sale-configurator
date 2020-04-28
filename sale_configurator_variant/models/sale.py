# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


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

    @api.multi
    @api.depends("variant_ids.product_uom_qty")
    def _compute_is_variant_qty_need_recompute(self):
        records = self.filtered("variant_ids")
        for record in records:
            qty = record._get_child_qty()
            record.is_variant_qty_need_recompute = qty != record.product_uom_qty

    def _get_child_qty(self):
        self.ensure_one()
        return sum(self.variant_ids.mapped("product_uom_qty"))

    @api.multi
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
        super(SaleOrderLine, self)._recompute_done(field)
        if field.name == "is_variant_qty_need_recompute":
            with_variant_qty = self.exists()._set_parent_variant_qty()
            with_variant_qty.write({"is_variant_qty_need_recompute": False})

    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, self)._get_price_config_subtotal()
        if self.parent_variant_id:
            res = 0
        elif self.variant_ids:
            for variant in self.variant_ids:
                res += variant.price_subtotal
        return res

    @api.model
    def _get_price_config_total(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, self)._get_price_config_total()
        if self.parent_variant_id:
            res = 0
        elif self.variant_ids:
            for variant in self.variant_ids:
                res += variant.price_total
        return res

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
        if self.product_tmpl_id.product_variant_count > 1:
            variant_lines = []
            for variant in self.product_tmpl_id.product_variant_ids:
                variant_lines.append((0, 0, self._prepare_sale_line_variant(variant)))
            self.variant_ids = variant_lines
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
