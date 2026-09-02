# Copyright 2021 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move"

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id, view_type, **options)
        if view_type == "form" and not self._context.get("force_original_move_form"):
            doc = etree.XML(res["arch"])

            for field in doc.xpath("//field[@name='invoice_line_ids']/list/field"):
                fname = field.get("name")
                field_def = self.env["account.move.line"]._fields.get(fname)
                if fname == "sequence" or not field_def or field_def.readonly:
                    continue

                # Make the Options lines readonly
                current = field.get("readonly")
                new_readonly = f"{current} or has_parent" if current else "has_parent"
                field.set("readonly", new_readonly)
            res["arch"] = etree.tostring(doc, pretty_print=True)
        return res
