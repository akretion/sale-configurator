# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_option_id = fields.Many2one("sale.order.line", "Parent Option")
    option_ids = fields.One2many("sale.order.line", "parent_option_id", "Options")
    
    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, line)._get_price_config_subtotal()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            res = 0
            for opt in self.option_ids:
                res += self.price_subtotal
        return res

    @api.model
    def _get_price_config_total(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, line)._get_price_config_total()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            res = 0
            for opt in self.option_ids:
                res += self.price_total
        return res
