# Copyright 2020 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    sale_min_qty = fields.Float(
        compute="_compute_sale_restricted_qty",
        store=True,
        string="Min Qty",
        digits="Product Unit of Measure",
    )
    manual_sale_min_qty = fields.Float(
        string="Manual Min Qty", digits="Product Unit of Measure"
    )
    sale_max_qty = fields.Float(
        compute="_compute_sale_restricted_qty",
        store=True,
        string="Max Qty",
        digits="Product Unit of Measure",
        help="High limit authorised in the sale line option",
    )
    manual_sale_max_qty = fields.Float(
        string="Manual Max Qty", digits="Product Unit of Measure"
    )

    @api.depends(
        "manual_sale_min_qty",
        "manual_sale_max_qty",
        "product_id",
        "product_id.sale_min_qty",
    )
    def _compute_sale_restricted_qty(self):
        for opt in self:
            opt.sale_min_qty = (
                opt.manual_sale_min_qty or opt.product_id.sale_min_qty or 0
            )
            opt.sale_max_qty = (
                opt.manual_sale_max_qty or opt.product_id.sale_max_qty or 0
            )
