# Copyright 2020 Akretion (http://www.akretion.com).
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    used_in_configurable_product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_used_in_configurable_product_ids",
        search="_search_used_in_configurable_product_ids",
    )
    used_in_configurable_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        compute="_compute_used_in_configurable_product_ids",
    )
    used_as_option_ids = fields.One2many(
        "product.configurator.option",
        "option_product_id",
        "Options made with this Product",
    )

    @api.depends("used_as_option_ids")
    def _compute_used_in_configurable_product_ids(self):
        for record in self:
            record.used_in_configurable_product_tmpl_ids = (
                record.used_as_option_ids.used_in_configurable_product_tmpl_ids
            )
            record.used_in_configurable_product_ids = (
                record.used_in_configurable_product_tmpl_ids.product_variant_ids
            )

    def _search_used_in_configurable_product_ids(self, operator, value):
        if operator != "=":
            raise UserError(_("Operator %s not supported") % operator)
        else:
            product = self.env["product.product"].browse(value)
            return [("id", "in", product.mapped("option_ids.option_product_id").ids)]
