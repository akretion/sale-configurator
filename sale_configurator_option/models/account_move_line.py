# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("sale_line_ids")
    def _compute_is_option(self):
        for rec in self:
            rec.is_option = any(
                [line.child_type == "option" for line in rec.sale_line_ids]
            )

    is_option = fields.Boolean(compute="_compute_is_option", store=True)
