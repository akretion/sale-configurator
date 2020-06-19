# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ProductConfiguratorTemplate(models.Model):
    _name = "product.configurator.template"
    _description = "Product Configurator Template"

    name = fields.Char('Name', index=True, required=True, translate=True)
    default_code = fields.Char('Internal Reference', index=True)
    description = fields.Text(
        'Description', translate=True)

    active = fields.Boolean('Active', default=True,
            help="If unchecked, it will allow you to hide\n"
                 "the Configurator Template without removing it.")
    configurable_option_ids = fields.One2many(
        "product.configurator.option",
        "product_conf_tmpl_id",
        "Configurable Option Lines",
        copy=True,
    )
