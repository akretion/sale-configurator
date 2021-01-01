# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


# TODO for now we simply round with integer qty
# see when we will have the case to support float qty
# but not sure we will have the case so let's see latter
def round_up(val):
    rounded_qty = round(val, 0)
    if rounded_qty <= val:
        return rounded_qty
    else:
        return rounded_qty + 1


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_delivered_method = fields.Selection(
        selection_add=[("option_proportional", "Proportional Option")]
    )

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        for line in self:
            if line.parent_option_id:
                continue
            else:
                super(SaleOrderLine, line)._action_launch_stock_rule(
                    previous_product_uom_qty=previous_product_uom_qty
                )
        return True

    @api.depends("parent_option_id.qty_delivered")
    def _compute_qty_delivered(self):
        for line in self:
            if line.qty_delivered_method == "option_proportional":
                parent = line.parent_option_id
                if parent.qty_delivered == parent.product_uom_qty:
                    line.qty_delivered = line.product_uom_qty
                else:
                    line.qty_delivered = min(
                        line.product_uom_qty,
                        round_up(
                            parent.qty_delivered
                            / parent.product_uom_qty
                            * line.product_uom_qty
                        ),
                    )
            else:
                super(SaleOrderLine, line)._compute_qty_delivered()

    def _get_compute_delivered_method(self):
        return "option_proportional"

    @api.depends("parent_option_id")
    def _compute_qty_delivered_method(self):
        for line in self:
            if line.parent_option_id:
                line.qty_delivered_method = line._get_compute_delivered_method()
            else:
                super(SaleOrderLine, line)._compute_qty_delivered_method()
