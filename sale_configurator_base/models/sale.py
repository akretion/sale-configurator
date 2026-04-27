# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    main_line_ids = fields.One2many(
        "sale.order.line", "order_id", domain=[("parent_id", "=", False)]
    )

    is_config_type = fields.Boolean(compute="_compute_is_config_type", store=True)

    hide_subtotal = fields.Boolean(compute="_compute_hide_subtotal")

    @api.depends("order_line.config_type")
    def _compute_is_config_type(self):
        for rec in self:
            rec.is_config_type = any(rec.order_line.mapped("config_type"))

    @api.depends("order_line.hide_subtotal")
    def _compute_hide_subtotal(self):
        for rec in self:
            rec.hide_subtotal = all(rec.order_line.mapped("hide_subtotal"))

    def copy_data(self, default=None):
        # Option lines should not be copied directly but from parent line option_ids
        if default is None:
            default = {}
        if "order_line" not in default:
            default["order_line"] = [
                (0, 0, line.copy_data()[0])
                for line in self.order_line.filtered(
                    lambda line: not line.is_downpayment and not line.parent_id
                )
            ]
        return super().copy_data(default)

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

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)

        if view_type == "form" and not self._context.get("force_original_sale_form"):
            doc = etree.XML(res["arch"])

            for field in doc.xpath("//field[@name='order_line']/list/field"):
                fname = field.get("name")
                field_def = self.env["sale.order.line"]._fields.get(fname)
                if fname == "sequence" or not field_def or field_def.readonly:
                    continue

                # Make the Options and Configurable Products readonly
                current = field.get("readonly", "")
                new_readonly = f"{current} or config_type" if current else "config_type"
                field.set("readonly", new_readonly)
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
        precompute=True,
    )
    # Becarefull, never use child_ids in computed field, use get_children() instead
    # to avoid duplicates and confusions between NewId records and real records.
    child_ids = fields.One2many("sale.order.line", "parent_id", "Children Lines")

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

    # This duplicated field is required because Odoo's native field is named
    # "order_partner_id" and we need a field explicitly named "partner_id" with the
    # same value.
    #
    # We extract the sale.order.line list and form views from the native
    # sale.order form and reuse them in our own views. These extracted views
    # contain references to "parent.partner_id".
    #
    # In our context, the parent is not the sale.order (order_id) but another
    # sale.order.line. As it is simpler to keep these "parent.partner_id" references,
    # we provide this mirrored field for compatibility.
    partner_id = fields.Many2one(related="order_id.partner_id", string="Order Customer")

    # Add items to this Selection for any new type of children.
    # (cf sale_configurator_option for example)
    config_type = fields.Selection(
        [("configurable", "Configurable")],
        string="Configuration type",
        help="Defines whether the line refers to a configurable product or "
        "to one of its child items ('option', 'variant', etc.)",
        compute="_compute_config_type",
        store=True
    )

    report_line_is_empty_parent = fields.Boolean(
        compute="_compute_report_line_is_empty_parent",
        help="Technical field used in the report to hide subtotals"
        " and taxes in case a parent line (with children lines) "
        "has no price by itself",
    )
    hide_subtotal = fields.Boolean(compute="_compute_hide_subtotal")

    @api.depends("child_ids", "price_unit", "parent_id")
    def _compute_hide_subtotal(self):
        for record in self:
            record.hide_subtotal = (
                record.child_ids
                and not record.price_unit
                or not record.parent_id
                and not record.child_ids
            )

    def _compute_parent(self):
        for record in self:
            record.parent_id = None

    def _get_child_type_sort(self):
        return []

    def get_children(self):
        return self.browse(False)

    def _sort_children_line(self, done):
        types = self._get_child_type_sort()
        types.sort()
        for _position, child_type in types:
            for line in self.get_children().sorted("sequence"):
                if line.config_type == child_type:
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
    def _compute_config_type(self):
        for record in self:
            record.config_type = record._get_config_type()

    def _get_config_type(self):
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

    @api.depends("price_subtotal", "price_total", "parent_id")
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
            # Children lines created from the wizard are linked to their
            # parent's order_id here
            parent_id = self._get_parent_id_from_vals(vals)
            if parent_id and "order_id" not in vals:
                vals["order_id"] = self.browse(parent_id).order_id.id
        return super().create(vals_list)
