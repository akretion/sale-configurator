# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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
        "Line is a configurable Product ?", compute="_compute_is_configurable",
    )

    @api.depends("product_id")
    def _compute_is_configurable(self):
        for record in self:
            record.is_configurable = record._is_line_configurable()

    def _is_line_configurable(self):
        return False

    @api.depends("price_subtotal", "price_total")
    def _compute_config_amount(self):
        """
        Compute the config amounts of the SO line.
        """
        for line in self:
            line.update(
                {
                    "price_config_subtotal": line._get_price_config_subtotal(),
                    "price_config_total": line._get_price_config_total(),
                }
            )

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

    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        self.ensure_one()
        return self.price_subtotal

    @api.model
    def _get_price_config_total(self):
        """
        get the config total amounts of the SO line.
        """
        self.ensure_one()
        return self.price_total
