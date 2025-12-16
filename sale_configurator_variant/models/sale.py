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
    config_type = fields.Selection(
        selection_add=[("variant", "Variant")],
        ondelete={"variant": "set null"},
    )
    variant_ids = fields.One2many(
        "sale.order.line",
        "parent_variant_id",
        "Variants",
        context={"default_config_type": "variant"},
        copy=True,
    )
    is_configurable_with_variant = fields.Boolean("With variants?")

    @api.depends("parent_variant_id")
    def _compute_parent(self):  # pylint: disable=missing-return
        for record in self:
            if record.parent_variant_id:
                record.parent_id = record.parent_variant_id
            else:
                super(SaleOrderLine, record)._compute_parent()

    @api.depends("variant_ids.product_uom_qty")
    def _compute_product_uom_qty(self):  # pylint: disable=missing-return
        """Parent's quantity is the sum of its Variants quantities."""
        super()._compute_product_uom_qty()

        for record in self:
            if record.variant_ids:
                record.product_uom_qty = record._get_child_qty()

    def _get_child_qty(self):
        self.ensure_one()
        return sum(self.variant_ids.mapped("product_uom_qty"))

    @api.depends("parent_variant_id", "parent_variant_id.product_uom_qty")
    def _compute_pricelist_item_id(self):  # pylint: disable=missing-return
        """Compute Variant's price_unit based on its Parent's quantity and UoM."""
        super()._compute_pricelist_item_id()
        for line in self:
            parent_variant = line.parent_variant_id
            if parent_variant and parent_variant.product_template_id:
                line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
                    parent_variant.product_template_id,
                    quantity=parent_variant.product_uom_qty or 1.0,
                    uom=parent_variant.product_uom,
                    date=line._get_order_date(),
                )

    @api.depends("parent_variant_id.product_uom_qty")
    def _compute_price_unit(self):  # pylint: disable=missing-return
        super()._compute_price_unit()
        for rec in self:
            if rec.variant_ids:
                rec.price_unit = 0

    @api.depends("variant_ids")
    def _compute_report_line_is_empty_parent(self):  # pylint: disable=missing-return
        super()._compute_report_line_is_empty_parent()

    @api.depends("variant_ids.price_subtotal", "variant_ids.price_total")
    def _compute_config_amount(self):  # pylint: disable=missing-return
        super()._compute_config_amount()

    @api.depends("product_template_id")
    def _compute_config_type(self):  # pylint: disable=missing-return
        super()._compute_config_type()

    @api.onchange("product_template_id")
    def product_tmpl_id_change(self):
        self.variant_ids = False
        if self.product_template_id:
            self.product_id = self.product_template_id.product_variant_id
            self.product_uom = self.product_template_id.uom_id

    def get_children(self):
        return super().get_children() + self.variant_ids

    def _get_child_type_sort(self):
        res = super()._get_child_type_sort()
        res.append((20, "variant"))
        return res

    def _get_config_type(self):
        if self.parent_variant_id:
            return "variant"
        elif self.is_configurable_with_variant:
            return "configurable"
        else:
            return super()._get_config_type()

    def _get_child_qty(self):
        self.ensure_one()
        return sum(self.variant_ids.mapped("product_uom_qty"))

    def _get_parent_id_from_vals(self, vals):
        if vals.get("parent_variant_id"):
            return vals["parent_variant_id"]
        else:
            return super()._get_parent_id_from_vals(vals)

    def _get_sale_order_line_multiline_description_sale(self):
        """Keep only product.template's name in sale.order.line's description
        for the line of a configurable product with Variants"""

        if self.is_configurable_with_variant and self.product_template_id:
            description = super(
                SaleOrderLine, self.with_context(is_configurable_with_variant=True)
            )._get_sale_order_line_multiline_description_sale()

            # Force to recompute product_id's display_name after this change
            self.product_id.invalidate_recordset(["display_name"])
            return description

        return super()._get_sale_order_line_multiline_description_sale()

    @api.model_create_multi
    def create(self, vals_list):
        variants_list = [vals.pop("variant_ids", None) for vals in vals_list]
        lines = super().create(vals_list)

        # We ensure to write variants after all field on the main line are recomputed
        # otherwise 'variant_ids' is erased during the create
        if any(variants_list):
            for line, vals in zip(lines, variants_list, strict=False):
                if vals:
                    line.write({"variant_ids": vals})

        return lines

    def write(self, vals):
        super().write(vals)
        # As we write "variant_ids" at the end of the create, we need to define
        # the sequences of the newly created lines who have this parent/child hierarchy
        if "variant_ids" in vals:
            self.order_id.sync_sequence()
        return True
