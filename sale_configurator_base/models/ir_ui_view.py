# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging
from ast import literal_eval

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_sale_line_item(self, mode):
        return getattr(self, f"_get_sale_line_{mode}_item")()

    def add_field_in_tree(self, field):
        return field.get("name") != "price_config_subtotal"

    def _sl_field_have_invalid_attrs_parent_field(self, field):
        # If we have some attrs with that depend of parent field
        # we check if that field exist on sale order line
        # it's not perfect as the field can exist in the model
        # but not in the view. But checking the view is super complex
        # so checking the model should solve most of incompatibility case
        for _key, domain in literal_eval(field.get("attrs", "{}")).items():
            for item in domain:
                if len(item) == 3 and "parent" in item[0]:
                    field_name = item[0].replace("parent.", "")
                    if field_name not in self.env["sale.order.line"]._fields:
                        _logger.info(
                            f"Field {field.get('name')} depend on parent {field_name}"
                            "the field do not exist so we skip it"
                        )
                        return True
        return False

    def _get_sale_line_tree_item(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            ._fields_view_get()
        )
        doc = etree.XML(res["arch"])
        fields = doc.xpath("//field[@name='order_line']/tree/field")
        controls = doc.xpath("//field[@name='order_line']/tree/control")
        items = []
        for field in fields:
            # We remove attrs on price_subtotal as they depend on field parent_id
            if field.get("name") in ["price_subtotal"]:
                field.set("attrs", "{}")
            # We skip fields with invalid attrs parent
            if self._sl_field_have_invalid_attrs_parent_field(field):
                continue
            # We remove this field that do not make sense on child view
            if self.add_field_in_tree(field):
                items.append(field)
        for clt in controls:
            items.append(clt)
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
