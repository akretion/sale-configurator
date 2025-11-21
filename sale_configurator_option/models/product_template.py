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
        help="Configurator template used to assign many Options at once to the current "
        "Configurable Product.",
    )
    # The Options of a Configurable Product (option_ids) can be defined
    # either by itss related Configurator Template's Options, or by its own
    # specific Options defined on the record.
    specific_option_ids = fields.One2many(
        "product.configurator.option",
        "configurable_product_tmpl_id",
        "Specific Options",
        copy=True,
        help="Options specific to the current Configurable Product",
    )
    option_ids = fields.One2many(
        "product.configurator.option",
        string="Options",
        compute="_compute_option_ids",
        copy=True,
        help="Options of the current Configurable Product\n"
        "(coming from the Configurator or specific to the Product)",
    )
    count_used_as_option = fields.Integer(
        compute="_compute_count_used_as_option",
        help="Number of configurator Options made with this product",
    )

    @api.depends("is_option")
    def _compute_is_not_sold_alone(self):
        for rec in self:
            rec.is_not_sold_alone = rec.is_option

    def _compute_count_used_as_option(self):
        for rec in self:
            rec.count_used_as_option = len(rec.product_variant_ids.used_as_option_ids)

    @api.depends("configurator_id")
    def _compute_option_ids(self):
        for rec in self:
            if rec.configurator_id:
                rec.option_ids = rec.configurator_id.option_ids
            else:
                rec.option_ids = rec.specific_option_ids
