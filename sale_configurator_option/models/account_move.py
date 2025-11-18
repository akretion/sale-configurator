# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """fields_view_get comes from Model (not AbstractModel)"""
        res = super().get_view(view_id, view_type, **options)
        if view_type == "form" and not self._context.get("force_original_move_form"):
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name='invoice_line_ids']/list/field"):
                if field.get("name") != "sequence":
                    current = field.get("readonly", "")
                    if current:
                        field.set("readonly", current + " or has_parent")
                    else:
                        field.set("readonly", "has_parent")
                if field.get("name") == "product_id":
                    field.set(
                        "class", field.get("class", "") + " configurator_option_padding"
                    )
                if field.get("name") == "name":
                    field.set(
                        "class", field.get("class", "") + " configurator_option_padding"
                    )
            res["arch"] = etree.tostring(doc, pretty_print=True)
        return res
