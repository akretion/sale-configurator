# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductConfiguratorOption(models.Model):
    _inherit = "product.configurator.option"

    included_by_option_id = fields.Many2one(
        "product.configurator.option",
        "Inclueded by Option",
        compute="_compute_included_by_option_id",
        store=True,
    )

    included_by_product_id = fields.Many2one(
        "product.product", "Inclueded by Product", domain=[("is_option", "=", True)]
    )
    included_option_ids = fields.One2many(
        "product.configurator.option", "included_by_option_id"
    )

    @api.one
    @api.constrains("included_by_product_id", "included_by_option_id")
    def _check_included_by_product_id(self):
        if self.included_by_product_id and not self.included_by_option_id:
            raise ValidationError(_("Included option must be defined first"))

    @api.multi
    @api.depends("included_by_product_id")
    def _compute_included_by_option_id(self):
        for option in self:
            included_by_option_id = self.env["product.configurator.option"].search(
                [
                    ("product_id", "=", option.included_by_product_id.id),
                    ("product_tmpl_id", "=", option.product_tmpl_id.id),
                ],
                limit=1,
            )
            option.included_by_option_id = included_by_option_id
