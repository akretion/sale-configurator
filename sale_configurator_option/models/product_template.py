# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_configurable_opt = fields.Boolean(
        "Is a Configurable Product ?",
        help="Check this, if the product is configurable with options",
    )
    is_option = fields.Boolean(
        "Is an Option Product ?",
        help="Check this, if the product is an option used in configurable product",
    )
    is_not_sold_alone = fields.Boolean(
        help="This Option can only be sold as part of a Configurable Product",
        default=False,
        compute="_compute_is_not_sold_alone",
        readonly=False,
        store=True,
    )
    configurator_id = fields.Many2one(
        "product.configurator.template",
        "Product Configurator Template",
        help="Template used to assign many Options at once to the current "
        "Configurable Product.",
    )
    # The Options of a Configurable Product (configurable_option_ids) can be defined
    # either by itss related Configurator Template's Options, or by its own
    # specific Options defined on the record.
    local_configurable_option_ids = fields.One2many(
        "product.configurator.option",
        "configurable_product_tmpl_id",
        "Specific Options",
        copy=True,
        help="Options specific to the current Configurable Product",
    )
    configurable_option_ids = fields.One2many(
        "product.configurator.option",
        string="Options",
        compute="_compute_configurable_option_ids",
        copy=True,
        help="Options for the current Configurable Product",
    )
    count_used_on_option_line = fields.Integer(
        "Count Use On Option Line", compute="_compute_count_used_on_option_line"
    )

    @api.depends("is_option")
    def _compute_is_not_sold_alone(self):
        for rec in self:
            rec.is_not_sold_alone = rec.is_option

    def _compute_count_used_on_option_line(self):
        for record in self:
            record.count_used_on_option_line = len(
                record.product_variant_ids.used_on_option_line_ids
            )

    @api.depends("configurator_id")
    def _compute_configurable_option_ids(self):
        for template in self:
            if template.configurator_id:
                template.configurable_option_ids = (
                    template.configurator_id.configurable_option_ids
                )
            else:
                template.configurable_option_ids = (
                    template.local_configurable_option_ids
                )
