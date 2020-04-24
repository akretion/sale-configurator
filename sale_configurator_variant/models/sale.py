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
    is_variant_qty_need_compute = fields.Boolean(
        compute="_compute_is_variant_qty_need_compute", store=True
    )
    parent_variant_qty = fields.Float(related="parent_variant_id.product_uom_qty",)

    @api.multi
    @api.depends("variant_ids.product_uom_qty")
    def _compute_is_variant_qty_need_compute(self):
        for record in self:
            record.is_variant_qty_need_compute = True

    @api.multi
    def _compute_parent_variant_qty(self):
        """
        This method is in charge of compute qty of parent variant
        sale order line
        """
        records = self.filtered("is_variant_qty_need_compute")
        for record in records:
            if record.variant_ids:
                record.product_uom_qty = 0
                for variant in self.variant_ids:
                    record.product_uom_qty += variant.product_uom_qty
        return records

    def _recompute_done(self, field):
        super(SaleOrderLine, self)._recompute_done(field)
        if field.name == "is_variant_qty_need_compute":
            # TOFIX insure one error we use for loop
            for var_qty in self.exists():
                with_variant_qty = var_qty._compute_parent_variant_qty()
            with_variant_qty.write({"is_variant_qty_need_compute": False})

    @api.multi
    def open_sale_line_config_variant(self):
        self.ensure_one()
        view_id = self.env.ref(
            "sale_configurator_variant.sale_order_line_config_variant_view_form"
        ).id
        return {
            "name": _("variant Configurator"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": self._name,
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "res_id": self.id,
        }

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
        }

    @api.onchange("product_tmpl_id")
    def product_tmpl_id_change(self):
        self.variant_ids = False
        if self.product_tmpl_id.product_variant_count > 1:
            variant_lines = []
            for variant in self.product_tmpl_id.product_variant_ids:
                variant_lines.append((0, 0, self._prepare_sale_line_variant(variant)))
            self.variant_ids = variant_lines
        return {}
