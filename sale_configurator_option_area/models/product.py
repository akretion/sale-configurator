# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _search_used_on_product_ids(self, operator, value):
        area_id = self._context.get("area_id")
        if area_id:
            options = (
                self.env["product.product"]
                .browse(value)
                .mapped("configurable_option_ids")
                .filtered(lambda s: s.area_id.id == area_id)
            )
            return [("id", "in", options.mapped("product_id").ids)]
        else:
            return super()._search_used_on_product_ids(operator, value)


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    area_id = fields.Many2one("product.configurator.option.area", string="Area")

    _sql_constraints = {
        (
            "product_tmpl_id_product_id_unique",
            "UNIQUE(product_tmpl_id,product_id,area_id)",
            "Option and Area must be unique by configurable product",
        )
    }


class ProductConfiguratorOptionArea(models.Model):
    _name = "product.configurator.option.area"
    _description = "Product Configurator Option Area"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    description = fields.Char()
    option_ids = fields.One2many("product.configurator.option", "area_id", "Option")
    product_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_product_ids",
        search="_search_product_ids",
    )

    def _compute_product_ids(self):
        for record in self:
            record.product_ids = record.mapped(
                "option_ids.used_on_product_tmpl.product_variant_ids"
            )

    def _search_product_ids(self, operator, value):
        if operator != "=":
            raise UserError(_("Operator %s not supported") % operator)
        else:
            product = self.env["product.product"].browse(value)
            return [("id", "in", product.mapped("configurable_option_ids.area_id").ids)]
