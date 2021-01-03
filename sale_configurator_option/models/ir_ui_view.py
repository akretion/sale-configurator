# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_sale_line_tree_field(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            ._fields_view_get()
        )
        doc = etree.XML(res["arch"])
        return doc.xpath("//field[@name='order_line']/tree/field")

    def _apply_view_inheritance(self, source, inherit_tree):
        # We use xmlid_to_res_id instead of env.ref to avoid a select sql request
        # done by the call to "exists()" in base code
        view_id = self.env["ir.model.data"].xmlid_to_res_id(
            "sale_configurator_option.sale_order_line_config_option_view_form_base"
        )
        if len(self) == 1 and self.id == view_id:
            node = source.xpath("//field[@name='option_ids']/tree")[0]
            for field in self._get_sale_line_tree_field():
                node.append(field)
        return super()._apply_view_inheritance(source, inherit_tree)
