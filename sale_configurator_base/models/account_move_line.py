# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "configurable.mixin"]

    @property
    def _lines_name(self):
        return "line_ids"

    @api.depends("line_ids")
    def _onchange_children_sequence(self):
        super()._onchange_children_sequence()


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["account.move.line", "configurable.line.mixin"]

    parent_id = fields.Many2one(
        "account.move.line", "Parent Line", ondelete="cascade", index=True
    )
    child_ids = fields.One2many("account.move.line", "parent_id", "Children Lines")

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
        return "move_id"
