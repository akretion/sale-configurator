# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    typology_ids = fields.Many2many(
        "product.configurator.option.typology",
        "prod_configurator_option_configurator_option_typology_rel",
        string="Option Typologies",
    )


class ProductConfiguratorOptionTypology(models.Model):
    _name = "product.configurator.option.typology"
    _description = "Product Configurator Option Typology"

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    description = fields.Char()
    logo = fields.Binary(attachment=True)
