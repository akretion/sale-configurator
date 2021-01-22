# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_alone_forbidden = fields.Boolean(compute="_compute_sale_alone_forbidden")

    # TODO make this configurable
    @api.depends("is_option")
    def _compute_sale_alone_forbidden(self):
        for record in self:
            record.sale_alone_forbidden = record.is_option

    @api.constrains(
        "available_in_pos",
        "local_configurable_option_ids.available_in_pos",
        "product_conf_tmpl_id.configurable_option_ids.available_in_pos",
    )
    def check_pos_availability(self):
        for record in self:
            for option in record.configurable_option_ids:
                if record.available_in_pos and not option.product_id.available_in_pos:
                    raise ValidationError(
                        _(
                            "The product '%s' can not be activated on POS if the option"
                            " '%s' is not activated in the pos"
                        )
                        % (record.name, option.product_id.name)
                    )
