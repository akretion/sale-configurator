# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_inheriting_views_to_complete(self):
        res = super()._get_inheriting_views_to_complete()
        res.append(
            (
                "sale_configurator_option.sale_order_line_config_option_view_form_base",
                "list",
                "//field[@name='child_option_ids']/list",
            )
        )
        return res
