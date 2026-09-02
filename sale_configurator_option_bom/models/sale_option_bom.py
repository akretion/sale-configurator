# Copyright 2024 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    related_option_id = fields.Many2one(
        "product.configurator.option",
        "Related Option",
        domain="[('configurable_product_tmpl_id', '=', parent_product_tmpl_id)]",
    )

    def _skip_bom_line(self, product, never_attribute_values=False):
        if self.related_option_id:
            return True
        else:
            return super()._skip_bom_line(product, never_attribute_values)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_moves_raw_values(self):
        moves = super()._get_moves_raw_values()

        for production in self:
            sol_options = production.sale_line_id.child_option_ids
            option_quantities = {
                sol.product_id.id: (sol.product_uom_qty, sol.product_uom)
                for sol in sol_options
            }

            bom_lines = production.bom_id.bom_line_ids.filtered_domain(
                [("related_option_id", "in", sol_options.option_id.ids)]
            )

            for bom_line in bom_lines:
                option_product = bom_line.related_option_id.product_id
                (qty_sold, sol_uom) = option_quantities.get(option_product.id)

                bom_uom = bom_line.product_uom_id
                qty_option_sold_bom_uom = sol_uom._compute_quantity(qty_sold, bom_uom)

                if qty_option_sold_bom_uom > 0.0:
                    total_qty_required = bom_line.product_qty * qty_option_sold_bom_uom
                    moves.append(
                        production._get_move_raw_values(
                            bom_line.product_id, total_qty_required, bom_uom
                        )
                    )
        return moves
