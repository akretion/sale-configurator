# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models

from odoo.addons.sale_configurator_base.models.sale import update_attrs


class AccountMoveLine(models.Model):
    _inherit = "account.move"

    @api.model
    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """ fields_view_get comes from Model (not AbstractModel) """
        res = super()._fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )
        if view_type == "form" and not self._context.get("force_original_move_form"):
            doc = etree.XML(res["arch"])
            for field in doc.xpath("//field[@name='invoice_line_ids']/tree/field"):
                if field.get("name") != "sequence":
                    update_attrs(
                        field,
                        {"readonly": [("is_option", "=", True)]},
                    )
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
