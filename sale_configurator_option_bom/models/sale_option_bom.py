# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    related_option_id = fields.Many2one(
        "product.configurator.option",
        "Option ref",
        domain="[('product_tmpl_id', '=', parent_product_tmpl_id)]",
    )

    def _skip_bom_line(self, product):

        if self.related_option_id:
            return True
        else:
            return super()._skip_bom_line(product)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()
        options = []
        for prod in self:
            lines = self.env["mrp.bom.line"].read_group(
                [
                    (
                        "related_option_id.id",
                        "in",
                        prod.sale_line_ids.option_ids.product_option_id.ids,
                    ),
                    ("bom_id", "=", prod.bom_id.id),
                ],
                fields=["product_qty:sum"],
                groupby=["product_id", "product_uom_id", "related_option_id"],
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
                list_lines = []
                list_product_id = []
                for line in lines:
                    for option in options:
                        if (
                            self.env["product.configurator.option"]
                            .browse(line["related_option_id"][0])
                            .product_id.id
                            == option["product_id"][0]
                        ):
                            total_qty_line = (
                                line["product_qty"] * option["product_uom_qty"]
                            )
                    if list_lines:
                        if line["product_id"][0] in list_product_id:
                            index_list_prod = list_product_id.index(
                                line["product_id"][0]
                            )
                            if (
                                list_lines[index_list_prod]["product_id"][0]
                                == line["product_id"][0]
                                and list_lines[index_list_prod]["product_uom_id"][0]
                                == line["product_uom_id"][0]
                            ):
                                list_lines[index_list_prod]["product_qty"] = (
                                    list_lines[index_list_prod]["product_qty"]
                                    + total_qty_line
                                )
                            else:
                                list_lines.append(line)
                                list_lines[-1]["product_qty"] = total_qty_line
                                list_product_id.append(line["product_id"][0])
                    else:
                        list_lines.append(line)
                        list_product_id.append(line["product_id"][0])
                        list_lines[-1]["product_qty"] = total_qty_line
                for list_prod in list_lines:
                    moves.append(
                        prod._get_move_raw_values(
                            self.env["product.product"].browse(
                                list_prod["product_id"][0]
                            ),
                            list_prod["product_qty"],
                            self.env["uom.uom"].browse(list_prod["product_uom_id"][0]),
                        )
                    )
        return moves
