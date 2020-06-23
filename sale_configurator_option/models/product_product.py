# Copyright 2020 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    option_of_product_ids = fields.Many2many(
        comodel_name='product.product',
        compute='_compute_option_of_product_ids',
        search='_search_option_of_product_ids',
        )

    @api.multi
    def _compute_option_of_product_ids(self):
        for record in self:
            option_lines = self.env['product.configurator.option'].search([
                ('product_id', '=', record.id)
                ])
            products = self.env['product.product'].browse(False)
            for option_line in option_lines:
                if option_line.product_tmpl_id:
                    products |=\
                        option_line.product_tmpl_id.product_variant_ids
            record.option_of_product_ids = products.ids

    def _search_option_of_product_ids(self, operator, value):
        if operator != '=':
            raise UserError(_("Operator %s not supported") % operator)
        else:
            product = self.env['product.product'].browse(value)
            return [
                ('id', 'in',
                 product.mapped('configurable_option_ids.product_id').ids)]
