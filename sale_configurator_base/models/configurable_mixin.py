# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class ConfigurableMixin(models.AbstractModel):
    """
    Justification for this model is that we want identical functionality
    on sale orders and invoices. We can't implement everything out of the
    box, so some re-implementing is necessary when inheriting the mixin.
    To implement, define:
    - @api.depends functions
    - _lines_name property
    """

    _name = "configurable.mixin"
    _description = "Configurable Mixin"

    @property
    def _lines_name(self):
        raise NotImplementedError

    @property
    def _lines(self):
        return getattr(self, self._lines_name)

    def sync_sequence(self):
        for record in self:
            done = []
            lines = record._lines.sorted("sequence")
            for line in lines:
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
        if self._lines_name in vals:
            self.sync_sequence()
        return True

    # @api.depends("lines")
    def _onchange_children_sequence(self):
        """Implement using @api.depends
        <sale.order/account.move>.line"""
        self.sync_sequence()


class ConfigurableLineMixin(models.AbstractModel):
    """
    To implement, define:
    - parent_id
    - child_ids
    - _parent_container property
    - @api.depends functions
    TODO cleanup???:
    - reimplement price_config_subtotal and total as fields.Monetary
    """

    _name = "configurable.line.mixin"
    _description = "Configurable Line Mixin"

    child_type = fields.Selection([])
    # Monetary fields require a currency, so reimplement it
    # TODO do something more elegant
    price_config_subtotal = fields.Float(
        compute="_compute_config_amount",
        string="Config Subtotal",
        readonly=True,
        store=True,
    )
    price_config_total = fields.Float(
        compute="_compute_config_amount",
        string="Config Total",
        readonly=True,
        store=True,
    )

    is_configurable = fields.Boolean(
        "Line is a configurable Product ?",
        compute="_compute_is_configurable",
    )
    report_line_is_empty_parent = fields.Boolean(
        compute="_compute_report_line_is_empty_parent",
        help="Technical field used in the report to hide subtotals"
        " and taxes in case a parent line (with children lines) "
        "has no price by itself",
    )

    @property
    def _parent_container(self):
        return getattr(self, self._parent_container_name)

    @property
    def _parent_container_name(self):
        raise NotImplementedError

    def _get_child_type_sort(self):
        return []

    def _sort_children_line(self, done):
        types = self._get_child_type_sort()
        types.sort()
        for _position, child_type in types:
            for line in self.child_ids.sorted("sequence"):
                if line.child_type == child_type:
                    line.sequence = len(done)
                    done.append(line)

    # @api.depends("price_unit", "child_ids")
    def _compute_report_line_is_empty_parent(self):
        for rec in self:
            rec.report_line_is_empty_parent = False
            price_unit_like_zero = (
                float_compare(rec.price_unit, 0.00, precision_digits=2) == 0
            )
            if rec.child_ids and price_unit_like_zero:
                rec.report_line_is_empty_parent = True

    # @api.depends("product_id")
    def _compute_is_configurable(self):
        for record in self:
            record.is_configurable = record._is_line_configurable()

    def _is_line_configurable(self):
        raise NotImplementedError

    # @api.depends(
    #     "price_subtotal",
    #     "price_total",
    #     "child_ids.price_subtotal",
    #     "child_ids.price_total",
    #     "parent_id",
    # )
    def _compute_config_amount(self):
        """
        Compute the config amounts of the line.
        Implement using @api.depends:
        - price_subtotal
        - price_total
        - child_ids.price_subtotal
        - child_ids.price_total
        - parent_id
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
        parent_name = self._parent_container_name
        for vals in vals_list:
            if vals.get("parent_id") and parent_name not in vals:
                vals[parent_name] = self.browse(vals["parent_id"])._parent_container.id
        return super().create(vals_list)
