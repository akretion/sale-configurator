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

    def _get_sale_line_item(self, view_type):
        return getattr(self, f"_get_sale_line_{view_type}_item")()

    def add_field_in_list(self, field):
        return field.get("name") != "price_config_subtotal"

    def _sl_field_have_invalid_attrs_parent_field(self, field):
        # If we have some attrs depending on a parent field
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
                            f"Field {field.get('name')} depends on parent {field_name}"
                            "the field do not exist so we skip it"
                        )
                        return True
        return False

    def _get_sale_line_list_item(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            .get_view()
        )
        doc = etree.XML(res["arch"])
        fields = doc.xpath("//field[@name='order_line']/list/field")
        items = []
        for field in fields:
            # We remove attrs on price_subtotal as they depend on field parent_id
            if field.get("name") in ["price_subtotal"]:
                field.set("attrs", "{}")
            # We skip fields with invalid attrs parent
            if self._sl_field_have_invalid_attrs_parent_field(field):
                continue
            # We remove this field that do not make sense on child view
            if self.add_field_in_list(field):
                items.append(field)
        return items

    def _get_sale_line_form_item(self):
        res = (
            self.env["sale.order"]
            .with_context(force_original_sale_form=True)
            .get_view()
        )
        arch = res["arch"].replace("parent.", "")
        doc = etree.XML(arch)
        node = doc.xpath("//field[@name='order_line']/form")[0]
        return node.getchildren()

    def _get_inheriting_views_to_complete(self):
        """Return a list of 3-tuple giving information on which inheriting view
        has to be completed and how to complete it:
        1) the XMLID of the view to be completed
        2) the view type ("form" or "list") of the sale.order.line's view to be added
        3) the xpath locating where the sale.order.line's view as to be added"""

        # To be overriden in other modules.
        # Cf sale_configurator_option or sale_configurator_variant
        return []

    def apply_inheritance_specs(self, source, specs_tree, pre_locate=lambda s: True):
        """Hack to add dynamically a sale.order.line's view on inheriting views
        as defined if the original sale.
        """

        for xmlid, view_type, xpath in self._get_inheriting_views_to_complete():
            view_id = self.env["ir.model.data"]._xmlid_to_res_id(xmlid)
            if self.id == view_id:
                node = specs_tree.xpath(xpath)[0]
                for item in self._get_sale_line_item(view_type):
                    node.append(item)

        return super().apply_inheritance_specs(source, specs_tree, pre_locate)

    def _add_validation_flag(self, combined_arch, view=None, arch=None):
        """Hack to add dynamically a sale.order.line's view on
        the Configurator base view `sale_order_line_config_base_view_form`"""

        # We override `_add_validation_flag` in order to complete the Configurator
        # base view because `apply_inheritance_specs` only acts on inheriting views
        # whereas `_add_validation_flag` acts on the arch of the root primary view
        # (param `combined_arch`) in the new `_combine()` method
        # in odoo/addons/base/models/ir_ui_view.py.

        xmlid_base = "sale_configurator_base.sale_order_line_config_base_view_form"
        view_base_id = self.env["ir.model.data"]._xmlid_to_res_id(xmlid_base)

        # The check on `not view and not arch` guarantees that `combined_arch` is the
        # arch of a primary view (cf the use of `_add_validation_flag` in `_combine`).
        if self.id == view_base_id and not view and not arch:
            node = combined_arch.xpath("//form")[0]
            for item in self._get_sale_line_item("form"):
                node.append(item)

        return super()._add_validation_flag(combined_arch, view, arch)
