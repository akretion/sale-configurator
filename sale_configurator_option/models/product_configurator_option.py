# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductConfiguratorOption(models.Model):
    _name = "product.configurator.option"
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = "Product Configurator Option"

    # An Option's parent can be either a configurator.template or a product.template
    configurator_id = fields.Many2one(
        "product.configurator.template",
        "Parent Configurator Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
    )
    configurable_product_tmpl_id = fields.Many2one(
        "product.template",
        "Parent Configurable Product Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        "Product",
        required=True,
        domain=[("is_option", "=", True)],
    )
    option_product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        string="Product Template",
        store=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        related="product_id.uom_id",
        help="Informative Unit of Measure, just to be displayed in Options views. "
        "Not used technically",
    )

    sequence = fields.Integer(
        default=1, help="Gives the sequence order when displaying."
    )
    is_default_option = fields.Boolean(help="Add this option by default.")
    option_qty_type = fields.Selection(
        [
            ("proportional_qty", "Proportional Qty"),
            ("independent_qty", "Independent Qty"),
        ],
        default="proportional_qty",
        required=True,
    )
    used_in_configurable_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Configurable Products using this Option",
        compute="_compute_used_on_product_template",
    )
    active = fields.Boolean(compute="_compute_active", store=True)

    @api.depends(
        "product_id.active",
        "configurable_product_tmpl_id.active",
        "configurator_id.active",
    )
    def _compute_active(self):
        for record in self:
            record.active = record.product_id.active and (
                record.configurable_product_tmpl_id.active
                or record.configurator_id.active
            )

    def _compute_used_on_product_template(self):
        for record in self:
            record.used_in_configurable_product_tmpl_ids = (
                record.configurable_product_tmpl_id
                + record.configurator_id.configurable_product_tmpl_ids
            )

    _sql_constraints = {
        (
            "configurable_product_tmpl_id_product_id_unique",
            "UNIQUE(configurable_product_tmpl_id,product_id)",
            "Option must be unique by configurable product",
        )
    }
