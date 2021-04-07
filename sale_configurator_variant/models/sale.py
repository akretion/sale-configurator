# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    child_type = fields.Selection(
        selection_add=[("variant", "Variant")],
        ondelete={"variant": "set null"},
    )
    variant_ids = fields.One2many(
        "sale.order.line",
        "parent_id",
        "Variants",
        domain=[("child_type", "=", "variant")],
        context={"default_child_type": "variant"},
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        domain=[("sale_ok", "=", True)],
        change_default=True,
        ondelete="restrict",
    )
    parent_qty = fields.Float(related="parent_id.product_uom_qty", readonly=False)
    is_multi_variant_line = fields.Boolean(
        "Multi variant",
    )
    price_unit = fields.Float(
        compute="_compute_price_unit",
        readonly=False,
        store=True,
    )

    def _get_sale_line_price_variant(self):
        product = self.product_id.with_context(
            partner=self.order_id.partner_id,
            quantity=self.parent_id.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.parent_id.product_uom.id,
        )
        return self.env["account.tax"]._fix_tax_included_price_company(
            self._get_display_price(product),
            self.product_id.taxes_id,
            self.tax_id,
            self.company_id,
        )

    @api.depends("parent_id.product_uom_qty", "product_id")
    def _compute_price_unit(self):
        for record in self:
            if record.child_type == "variant":
                record.price_unit = record._get_sale_line_price_variant()

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
        if self.parent_id:
            return False
        elif self.is_multi_variant_line:
            return True
        else:
            return super()._is_line_configurable()

    def _get_child_qty(self):
        self.ensure_one()
        return sum(self.variant_ids.mapped("product_uom_qty"))

    @api.onchange("product_tmpl_id")
    def product_tmpl_id_change(self):
        self.variant_ids = False
        if self.product_tmpl_id:
            # ToFIX set product_id to False raise error on[
            #  _sql_constraints = accountable_required_fields
            self.product_id = self.product_tmpl_id.product_variant_id

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()
        if self.product_tmpl_id:
            self.name = self.product_tmpl_id.name
        return res
