# Copyright 2021 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_option_message = fields.Boolean(compute="_compute_has_option_message")

    @api.depends("order_line")
    def _compute_has_option_message(self):
        for record in self:
            record.has_option_message = any(
                record.order_line.mapped("product_option_id.has_message")
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    option_message = fields.Char(string="Message")

    has_option_message = fields.Boolean(compute="_compute_has_option_message")

    @api.depends("product_option_id")
    def _compute_has_option_message(self):
        for record in self:
            record.has_option_message = (
                record.product_option_id and record.product_option_id.has_message
            )

    @api.constrains("option_message")
    def _check_option_message_has_option_message(self):
        for record in self:
            if record.has_option_message and not record.option_message:
                raise ValidationError(
                    _("Message is mandatory for an option with message: %s.")
                    % record.product_option_id.product_id.name
                )
            if not record.has_option_message and record.option_message:
                raise ValidationError(
                    _("Can't set message on option without message: %s.")
                    % record.product_option_id.product_id.name
                )
