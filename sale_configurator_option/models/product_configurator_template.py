# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductConfiguratorTemplate(models.Model):
    _name = "product.configurator.template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product Configurator Template"
    _order = "name"

    name = fields.Char(index=True, required=True, translate=True)
    code = fields.Char("Internal Reference", index=True)
    description = fields.Text(translate=True)

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide\n"
        "the Configurator Template without removing it.",
    )
    configurable_option_ids = fields.One2many(
        "product.configurator.option",
        "configurator_id",
        "Configurable Option Lines",
        copy=True,
    )
    product_tmpl_ids = fields.One2many(
        "product.template",
        "configurator_id",
        "Product Templates",
        help="All the configurable Product Templates following this Configurator",
    )
