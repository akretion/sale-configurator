# Copyright 2025 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _get_combination_name(self):
        """Keep only product.template's name in sale.order.line's description
        for the line of a configurable product with Variants"""
        res = super()._get_combination_name()
        if self._context.get("is_multi_variant_line"):
            return ""

        return res
