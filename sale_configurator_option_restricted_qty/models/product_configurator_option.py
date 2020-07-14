# Copyright 2020 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    sale_min_qty = fields.Float(
        string="Min Qty", default=0, digits=dp.get_precision("Product Unit of Measure")
    )
    sale_max_qty = fields.Float(
        string="Max Qty",
        oldname="max_qty",
        default=1,
        digits=dp.get_precision("Product Unit of Measure"),
        help="High limit authorised in the sale line option",
    )

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if self.product_id:
            self.sale_min_qty = self.product_id.sale_min_qty
            self.sale_max_qty = self.product_id.sale_max_qty
        return res
