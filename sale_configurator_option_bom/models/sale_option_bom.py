# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    related_option = fields.Many2one("product.product", "Option ref")

    def _skip_bom_line(self, product):
        res = super()._skip_bom_line(product)

        if self.related_option:
            return True
        else:
            return res


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()
        options = []

        for prod in self:
            lines = self.env["mrp.bom.line"].read_group(
                [
                    (
                        "related_option.id",
                        "in",
                        prod.sale_line_ids.option_ids.product_id.ids,
                    ),
                    ("parent_product_tmpl_id.id", "=", prod.product_tmpl_id.id),
                ],
                fields=["product_qty:sum"],
                groupby=["product_id", "product_uom_id", "related_option"],
                lazy=False,
            )
            options = self.env["sale.order.line"].read_group(
                [
                    ("product_id.type", "=", "service"),
                    ("id", "in", prod.sale_line_ids.option_ids.ids),
                ],
                fields=["product_uom_qty:sum"],
                groupby=["product_id", "product_uom"],
                lazy=False,
            )
            if lines:
                List_lines = []
                list_product_id = []
                for line in lines:
                    for option in options:
                        if line["related_option"][0] == option["product_id"][0]:
                            total_qty_line = (
                                line["product_qty"] * option["product_uom_qty"]
                            )
                    if List_lines:
                        if line["product_id"][0] in list_product_id:
                            index_list_prod = list_product_id.index(
                                line["product_id"][0]
                            )
                            if (
                                List_lines[index_list_prod]["product_id"][0]
                                == line["product_id"][0]
                                and List_lines[index_list_prod]["product_uom_id"][0]
                                == line["product_uom_id"][0]
                            ):
                                List_lines[index_list_prod]["product_qty"] = (
                                    List_lines[index_list_prod]["product_qty"]
                                    + total_qty_line
                                )
                            else:
                                List_lines.append(line)
                                List_lines[-1]["product_qty"] = total_qty_line
                                list_product_id.append(line["product_id"][0])
                    else:
                        List_lines.append(line)
                        list_product_id.append(line["product_id"][0])
                        List_lines[-1]["product_qty"] = total_qty_line
                for List_prod in List_lines:
                    moves.append(
                        prod._get_move_raw_values(
                            self.env["product.product"].browse(
                                List_prod["product_id"][0]
                            ),
                            List_prod["product_qty"],
                            self.env["uom.uom"].browse(List_prod["product_uom_id"][0]),
                        )
                    )
        return moves
