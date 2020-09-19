# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_configurable_opt = fields.Boolean(
        "Is a Configurable Product ?",
        help="Chek this, if the product is configurable with options",
    )
    is_option = fields.Boolean(
        "Is an Option Product ?",
        help="Chek this, if the product is an option used in configurable product",
    )
    product_conf_tmpl_id = fields.Many2one(
        "product.configurator.template", "Related Configurable Template",
    )
    local_configurable_option_ids = fields.One2many(
        "product.configurator.option",
        "product_tmpl_id",
        "Specific Configurable Option Lines",
        copy=True,
    )
    configurable_option_ids = fields.One2many(
        "product.configurator.option",
        string="Configurable Option Lines",
        compute="_compute_configurable_option_ids",
        copy=True,
    )

    @api.multi
    @api.depends("product_conf_tmpl_id")
    def _compute_configurable_option_ids(self):
        for template in self:
            if template.product_conf_tmpl_id:
                template.configurable_option_ids = (
                    template.product_conf_tmpl_id.configurable_option_ids
                )
            else:
                template.configurable_option_ids = (
                    template.local_configurable_option_ids
                )
