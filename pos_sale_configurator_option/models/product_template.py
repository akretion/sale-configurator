# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_alone_forbidden = fields.Boolean(compute="_compute_sale_alone_forbidden")

    # TODO make this configurable
    @api.depends("is_option")
    def _compute_sale_alone_forbidden(self):
        for record in self:
            record.sale_alone_forbidden = record.is_option
