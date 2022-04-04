# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast

from lxml import etree

from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.tools import float_compare


# TODO put this in a box tool module
def update_attrs(node, add_attrs):
    attrs = ast.literal_eval(node.get("attrs", "{}").replace("\n", "").strip())
    for key in add_attrs:
        attrs[key] = expression.OR([attrs.get(key, []), add_attrs[key]])
    node.set("attrs", str(attrs))


class SaleOrder(models.Model):
    _inherit = "sale.order"

    main_line_ids = fields.One2many(
        "sale.order.line", "order_id", domain=[("parent_id", "=", False)]
    )

    def sync_sequence(self):
        for record in self:
            done = []
            for line in record.order_line.sorted("sequence"):
                if not line.parent_id:
                    line.sequence = len(done)
                    done.append(line)
                    line._sort_children_line(done)

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

    @api.model
    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get comes from Model (not AbstractModel)"""
        res = super()._fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form" and not self._context.get("force_original_sale_form"):
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name='order_line']/tree/field"):
                fname = field.get("name")
                if fname != "sequence":
                    if not self.env["sale.order.line"]._fields[fname].readonly:
                        update_attrs(
                            field,
                            {
                                "readonly": [
                                    "|",
                                    ("parent_id", "!=", False),
                                    "&",
                                    ("is_configurable", "=", True),
                                    ("is_configured", "=", True),
                                ]
                            },
                        )
                if fname == "product_id":
                    field.set(
                        "class", field.get("class", "") + " configurator_option_padding"
                    )
                if fname == "name":
                    field.set(
                        "class",
                        field.get("class", "")
                        + " description configurator_option_padding",
                    )
            res["arch"] = etree.tostring(doc, pretty_print=True).decode("utf-8")
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_id = fields.Many2one(
        "sale.order.line",
        "Parent Line",
        ondelete="cascade",
        index=True,
        compute="_compute_parent",
        store=True,
    )
    # Becarefull never use child_ids in computed field because odoo is going
    # to do crazy thing, indead inside you will have duplicated data
    # (with real id and with Newid) so please instead use get_children method
    # child_ids is used for reporting
    child_ids = fields.One2many("sale.order.line", "parent_id", "Children Lines")
    child_type = fields.Selection([], compute="_compute_parent", store=True)
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
    # There is already an order_partner_id in the sale line class
    # but we want to make the view as much compatible between child view
    # wo want a native view do parent.partner_id we want to have the same behaviour
    # with the child line (but in that case the parent is a sale order line
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")

    is_configurable = fields.Boolean(
        "Line is a configurable Product ?",
        compute="_compute_is_configurable",
    )
    # Technical field to know if the line was created from the
    # Add Configurable Product interface
    is_configured = fields.Boolean(
        "Line is a configured Product ?",
    )
    report_line_is_empty_parent = fields.Boolean(
        compute="_compute_report_line_is_empty_parent",
        help="Technical field used in the report to hide subtotals"
        " and taxes in case a parent line (with children lines) "
        "has no price by itself",
    )
    product_uom_qty = fields.Float(
        compute="_compute_product_uom_qty",
        readonly=False,
        store=True,
    )

    # In different implementation the price unit can depend on other lines
    # So in the base module we add an empty generic implementation
    price_unit = fields.Float(
        compute="_compute_price_unit",
        readonly=False,
        store=True,
    )
    hide_subtotal = fields.Boolean(compute="_compute_hide_subtotal")

    def _compute_hide_subtotal(self):
        for record in self:
            record.hide_subtotal = (
                record.child_ids
                and not record.price_unit
                or not record.parent_id
                and not record.child_ids
            )

    def _compute_price_unit(self):
        pass

    def _compute_parent(self):
        for record in self:
            record.parent_id = None
            record.child_type = None

    def _compute_product_uom_qty(self):
        # inherit me to add specific behaviours
        pass

    def _get_child_type_sort(self):
        return []

    def get_children(self):
        return self.browse(False)

    def _sort_children_line(self, done):
        types = self._get_child_type_sort()
        types.sort()
        for _position, child_type in types:
            for line in self.get_children().sorted("sequence"):
                if line.child_type == child_type:
                    line.sequence = len(done)
                    done.append(line)

    @api.depends("price_unit")
    def _compute_report_line_is_empty_parent(self):
        for rec in self:
            rec.report_line_is_empty_parent = False
            price_unit_like_zero = (
                float_compare(rec.price_unit, 0.00, precision_digits=2) == 0
            )
            if rec.get_children() and price_unit_like_zero:
                rec.report_line_is_empty_parent = True

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
                + sum(self.get_children().mapped("price_subtotal")),
                "price_config_total": self.price_total
                + sum(self.get_children().mapped("price_total")),
            }

    def _get_parent_id_from_vals(self, vals):
        return False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            parent_id = self._get_parent_id_from_vals(vals)
            if parent_id and "order_id" not in vals:
                vals["order_id"] = self.browse(parent_id).order_id.id
        return super().create(vals_list)

    def write(self, vals):
        super().write(vals)
        if "option_ids" in vals:
            self.order_id.sync_sequence()
        return True
