# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_config_subtotal = fields.Monetary(compute='_compute_config_amount', string='Config Subtotal', readonly=True, store=True)
    price_config_total = fields.Monetary(compute='_compute_config_amount', string='Config Total', readonly=True, store=True)

    @api.depends('price_subtotal', 'price_total')
    def _compute_config_amount(self):
        """
        Compute the config amounts of the SO line.
        """
        for line in self:
            line.update({
                'price_config_subtotal': line._get_price_config_subtotal(),
                'price_config_total': line._get_price_config_total(),
            })

    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        self.ensure_one()
        return self.price_subtotal

    @api.model
    def _get_price_config_total(self):
        """
        get the config total amounts of the SO line.
        """
        self.ensure_one()
        return self.price_total
