# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_variant_id = fields.Many2one(
        "sale.order.line", string="Parent Variant", index=True
    )
    child_type = fields.Selection(
        selection_add=[("variant", "Variant")],
        ondelete={"variant": "set null"},
    )
    variant_ids = fields.One2many(
        "sale.order.line",
        "parent_variant_id",
        "Variants",
        context={"default_child_type": "variant"},
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        domain=[("sale_ok", "=", True)],
        change_default=True,
        ondelete="restrict",
    )
    is_multi_variant_line = fields.Boolean(
        "Multi variant",
    )
    discount = fields.Float(compute="_compute_discount", readonly=False, store=True)

    @api.depends("parent_variant_id")
    def _compute_parent(self):
        for record in self:
            if record.parent_variant_id:
                record.parent_id = record.parent_variant_id
                record.child_type = "variant"
            else:
                super(SaleOrderLine, record)._compute_parent()

    def _get_sale_line_price_variant(self):
        product = self.product_id.with_context(
            partner=self.order_id.partner_id,
            quantity=self.parent_variant_id.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.parent_variant_id.product_uom.id,
        )
        return self.env["account.tax"]._fix_tax_included_price_company(
            self._get_display_price(product),
            self.product_id.taxes_id,
            self.tax_id,
            self.company_id,
        )

    def _get_display_price(self, product):
        if self.variant_ids:
            return 0
        else:
            if self.parent_variant_id:
                self = self.with_context(
                    parent_variant_qty=self.parent_variant_id.product_uom_qty
                )
            return super()._get_display_price(product)

    @api.depends("parent_variant_id.product_uom_qty", "product_id")
    def _compute_price_unit(self):
        super()._compute_price_unit()
        for record in self:
            if record.parent_variant_id and record.product_id:
                record.price_unit = record._get_sale_line_price_variant()

    @api.depends("parent_variant_id.product_uom_qty")
    def _compute_discount(self):
        for record in self:
            if record.parent_variant_id and record.product_id:
                record._onchange_discount()

    @api.depends("variant_ids.product_uom_qty")
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for record in self:
            if record.variant_ids:
                record.product_uom_qty = record._get_child_qty()

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

    def _get_child_qty(self):
        self.ensure_one()
        # TODO clean on V16
        # hack to solve onchange issue
        variants = self.variant_ids.filtered(
            lambda s: not isinstance(s.id, models.NewId) or hasattr(s.id, "ref")
        )
        return sum(variants.mapped("product_uom_qty"))

    @api.onchange("product_tmpl_id")
    def product_tmpl_id_change(self):
        self.variant_ids = False
        if self.product_tmpl_id:
            # ToFIX set product_id to False raise error on[
            #  _sql_constraints = accountable_required_fields
            self.product_id = self.product_tmpl_id.product_variant_id
            self.product_uom = self.product_tmpl_id.uom_id

    def get_sale_order_line_multiline_description_sale(self, product):
        if self.product_tmpl_id:
            return self._get_product_template_description_sale()
        elif self.child_type == "variant":
            return self._get_product_variant_description_sale()
        else:
            return super().get_sale_order_line_multiline_description_sale(product)

    def _get_product_template_description_sale(self):
        return f"{self.product_tmpl_id.name}\n{self.product_tmpl_id.description_sale}"

    def _get_product_variant_description_sale(self):
        return self.product_id.display_name

    def _get_parent_id_from_vals(self, vals):
        if "parent_variant_id" in vals:
            return vals.get("parent_variant_id")
        else:
            return super()._get_parent_id_from_vals(vals)

    @api.depends("variant_ids")
    def _compute_report_line_is_empty_parent(self):
        super()._compute_report_line_is_empty_parent()

    @api.depends("variant_ids.price_subtotal", "variant_ids.price_total")
    def _compute_config_amount(self):
        super()._compute_config_amount()

    def get_children(self):
        return super().get_children() + self.variant_ids

    @api.onchange(
        "product_id", "price_unit", "product_uom", "product_uom_qty", "tax_id"
    )
    def _onchange_discount(self):
        if self.parent_variant_id:
            self = self.with_context(
                parent_variant_qty=self.parent_variant_id.product_uom_qty
            )
        return super()._onchange_discount()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        if self._context.get("parent_variant_qty"):
            qty = self._context.get("parent_variant_qty")
            product = product.with_context(quantity=qty)
        return super()._get_real_price_currency(
            product, rule_id, qty, uom, pricelist_id
        )
