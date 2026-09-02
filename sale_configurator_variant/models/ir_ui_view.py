# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

XMLID = "sale_configurator_variant.sale_order_line_config_variant_view_form_base"


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_inheriting_views_to_complete(self):
        res = super()._get_inheriting_views_to_complete()
        res.append((XMLID, "list", "//field[@name='variant_ids']/list"))
        return res
