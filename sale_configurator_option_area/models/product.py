# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    area_id = fields.Many2one("product.configurator.option.area", string="Area",)


class ProductConfiguratorOptionArea(models.Model):
    _name = "product.configurator.option.area"
    _description = "Product Configurator Option Area"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    description = fields.Char()
