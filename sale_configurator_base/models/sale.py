# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def sync_sequence(self):
        for record in self:
            count = 0
            for line in record.order_line.sorted("sequence"):
                if not line.parent_id:
                    line.sequence = count
                    count += 1
                    line._sort_children_line(count)

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

    parent_id = fields.Many2one(
        "sale.order.line", "Parent Line", ondelete="cascade", index=True
    )
    child_ids = fields.One2many("sale.order.line", "parent_id", "Children Lines")
    child_type = fields.Selection([])
    price_config_subtotal = fields.Monetary(
        compute="_compute_config_amount",
        string="Config Subtotal",
        readonly=True,
        store=True,
    )
    price_config_total = fields.Monetary(
        compute="_compute_config_amount",
        string="Config Total",
        readonly=True,
        store=True,
    )
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")
    is_configurable = fields.Boolean(
        "Line is a configurable Product ?",
        compute="_compute_is_configurable",
    )

    def _get_child_type_sort(self):
        return []

    def _sort_children_line(self, count):
        types = self._get_child_type_sort()
        types.sort()
        for _position, child_type in types:
            for line in self.child_ids:
                if line.child_type == child_type:
                    line.sequence = count
                    count += 1

    @api.depends("product_id")
    def _compute_is_configurable(self):
        for record in self:
            record.is_configurable = record._is_line_configurable()

    def _is_line_configurable(self):
        return False

    def save_add_product_and_close(self):
        return {"type": "ir.actions.act_window_close"}

    def save_add_product_and_new(self):
        return self.browse().open_sale_line_config_base()

    def open_sale_line_config_base(self):
        view_id = self.env.ref(
            "sale_configurator_base.sale_order_line_config_base_view_form"
        ).id
        return {
            "name": _("Base Configurator"),
            "type": "ir.actions.act_window",
            "context": self._context,
            "view_mode": "form",
            "res_model": self._name,
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "res_id": self.id,
        }

    @api.depends(
        "price_subtotal",
        "price_total",
        "child_ids.price_subtotal",
        "child_ids.price_total",
        "parent_id",
    )
    def _compute_config_amount(self):
        """
        Compute the config amounts of the SO line.
        """
        for line in self:
            line.update(line._get_price_config())

    def _get_price_config(self):
        self.ensure_one()
        if self.parent_id:
            return {
                "price_config_subtotal": 0,
                "price_config_total": 0,
            }
        else:
            return {
                "price_config_subtotal": self.price_subtotal
                + sum(self.child_ids.mapped("price_subtotal")),
                "price_config_total": self.price_total
                + sum(self.child_ids.mapped("price_total")),
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("parent_id") and "order_id" not in vals:
                vals["order_id"] = self.browse(vals["parent_id"]).order_id.id
        return super().create(vals_list)
