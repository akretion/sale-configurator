# Copyright 2021 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    has_message = fields.Boolean(string="Has message?", default=False)
