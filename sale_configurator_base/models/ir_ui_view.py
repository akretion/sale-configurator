# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from lxml import etree

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_sale_line_item(self, mode):
        return getattr(self, f"_get_sale_line_{mode}_item")()

    def _get_sale_line_tree_item(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            ._fields_view_get()
        )
        doc = etree.XML(res["arch"])
        fields = doc.xpath("//field[@name='order_line']/tree/field")
        items = []
        for field in fields:
            # We remove attrs on price_subtotal as they depend on field parent_id
            if field.get("name") in ["price_subtotal"]:
                field.set("attrs", "{}")
            # We remove this field that do not make sense on child view
            if field.get("name") != "price_config_subtotal":
                items.append(field)
        return items

    def _get_sale_line_form_item(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            ._fields_view_get()
        )
        arch = res["arch"].replace("parent.", "")
        doc = etree.XML(arch)
        node = doc.xpath("//field[@name='order_line']/form")[0]
        return node.getchildren()

    def _view_to_complete_dynamically(self):
        return [
            (
                "form",
                "sale_configurator_base.sale_order_line_config_base_view_form",
                "//sheet",
            )
        ]

    def _apply_view_inheritance(self, source, inherit_tree):
        for mode, xmlid, path in self._view_to_complete_dynamically():
            # We use xmlid_to_res_id instead of env.ref to avoid a select sql request
            # done by the call to "exists()" in base code
            view_id = self.env["ir.model.data"].xmlid_to_res_id(xmlid)
            if len(self) == 1 and self.id == view_id:
                node = source.xpath(path)[0]
                for item in self._get_sale_line_item(mode):
                    node.append(item)
        return super()._apply_view_inheritance(source, inherit_tree)
