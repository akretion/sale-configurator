# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

XMLID = "sale_configurator_variant.sale_order_line_config_variant_view_form_base"


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _view_to_complete_dynamically(self):
        res = super()._view_to_complete_dynamically()
        res.append(
            (
                "tree",
                XMLID,
                "//field[@name='variant_ids']/tree",
            )
        )
        return res
