# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from lxml import etree

from odoo import _, api, fields, models
from odoo.osv import expression


# TODO put this in a box tool module
def update_attrs(node, add_attrs):
    attrs = ast.literal_eval(node.get("attrs", "{}").replace("\n", "").strip())
    for key in add_attrs:
        attrs[key] = expression.OR([attrs.get(key, []), add_attrs[key]])
    node.set("attrs", str(attrs))


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["configurable.mixin", "sale.order"]

    @property
    def _lines_name(self):
        return "order_line"

    @api.depends("order_line")
    def _onchange_children_sequence(self):
        super()._onchange_children_sequence()

    @api.model
    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """ fields_view_get comes from Model (not AbstractModel) """
        res = super()._fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form" and not self._context.get("force_original_sale_form"):
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name='order_line']/tree/field"):
                if field.get("name") != "sequence":
                    update_attrs(
                        field,
                        {
                            "readonly": [
                                "|",
                                ("parent_id", "!=", False),
                                ("is_configurable", "=", True),
                            ]
                        },
                    )
                if field.get("name") == "product_id":
                    field.set(
                        "class", field.get("class", "") + " configurator_child_padding"
                    )
                if field.get("name") == "name":
                    field.set(
                        "class",
                        field.get("class", "")
                        + " description configurator_child_padding",
                    )
            res["arch"] = etree.tostring(doc, pretty_print=True).decode("utf-8")
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        """
        _create_invoices doesn't have the right hooks for us
        to directly build the parent/child relationships,
        thus we rebuild them at the end
        """
        result = super()._create_invoices(grouped, final, date)
        for invoice in result:
            invoice._rebuild_parent_configuration_from_sale()
        return result


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["configurable.line.mixin", "sale.order.line"]

    parent_id = fields.Many2one(
        "sale.order.line", "Parent Line", ondelete="cascade", index=True
    )
    child_ids = fields.One2many("sale.order.line", "parent_id", "Children Lines")
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")
    # There is already an order_partner_id in the sale line class
    # but we want to make the view as much compatible between child view
    # wo want a native view do parent.partner_id we want to have the same behaviour
    # with the child line (but in that case the parent is a sale order line
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")

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
        return super()._compute_config_amount()

    @api.depends("product_id")
    def _compute_is_configurable(self):
        return super()._compute_is_configurable()

    @api.depends("price_unit", "child_ids")
    def _compute_report_line_is_empty_parent(self):
        return super()._compute_report_line_is_empty_parent()

    @property
    def _parent_container_name(self):
        return "order_id"
