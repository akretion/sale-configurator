# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


import logging
import re

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_sale_line_item(self, view_type):
        return getattr(self, f"_get_sale_line_{view_type}_item")()

    def _extract_parent_field_name(self, expr):
        """Return the first field name referenced as 'parent.<field>'
        in an expression string, or False if there is none."""
        match = re.search(r"parent\.(\w+)", str(expr))
        return match.group(1) if match else False

    def _have_attr_with_invalid_parent_field(self, field):
        """Return whether a field attribute references a parent field that
        does not exist on sale.order.line.

        Such references are only valid on the sale.order view they come from;
        on the sale.order.line child view they would break validation, so the
        field must be skipped."""
        sol_fields = self.env["sale.order.line"]._fields
        for attr_name in ("column_invisible", "invisible", "readonly", "required"):
            field_name = self._extract_parent_field_name(field.get(attr_name, ""))
            if field_name and field_name not in sol_fields:
                _logger.info(
                    f"Field {field.get('name')} has attribute {attr_name} "
                    f"referencing parent {field_name}, a field that does not "
                    "exist on sale.order.line so we skip it"
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
            if self._have_attr_with_invalid_parent_field(field):
                continue
            if field.get("name") == "product_id" and field.get("optional") == "hide":
                field.set("optional", "show")
            # price_config_subtotal does not make sense on child view
            if field.get("name") != "price_config_subtotal":
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
