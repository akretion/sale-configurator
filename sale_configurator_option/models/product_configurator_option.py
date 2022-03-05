# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductConfiguratorOption(models.Model):
    _name = "product.configurator.option"
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = "Product Configurator Option"

    def _get_default_product_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order="id").id

    product_conf_tmpl_id = fields.Many2one(
        "product.configurator.template",
        "Parent Configurable Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
    )
    # TODO we should add a prefix => configurable_product_tmpl_id
    product_tmpl_id = fields.Many2one(
        "product.template",
        "Parent Product Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
    )
    # TODO we should add a prefix => option_product_id
    product_id = fields.Many2one(
        "product.product",
        "Option Product Variant",
        required=True,
        domain=[("is_option", "=", True)],
    )
    option_product_tmpl_id = fields.Many2one(
        related="product_id.product_tmpl_id",
        string="Option Product Template",
        store=True,
    )
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Product Unit of Measure",
        default=_get_default_product_uom_id,
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement"
        " for the inventory control",
    )
    sequence = fields.Integer(
        "Sequence", default=1, help="Gives the sequence order when displaying."
    )
    is_default_option = fields.Boolean(help="Add this option by default.")
    option_qty_type = fields.Selection(
        [
            ("proportional_qty", "Proportional Qty"),
            ("independent_qty", "Independent Qty"),
        ],
        string="Option qty Type",
        default="proportional_qty",
        required=True,
    )
    used_on_product_tmpl_ids = fields.Many2many(
        comodel_name="product.template",
        string="Used on product template",
        compute="_compute_used_on_product_template",
    )
    active = fields.Boolean(compute="_compute_active", store=True)

    @api.depends(
        "product_id.active", "product_tmpl_id.active", "product_conf_tmpl_id.active"
    )
    def _compute_active(self):
        for record in self:
            record.active = record.product_id.active and (
                record.product_tmpl_id.active or record.product_conf_tmpl_id.active
            )

    def _compute_used_on_product_template(self):
        for record in self:
            record.used_on_product_tmpl_ids = (
                record.product_tmpl_id + record.product_conf_tmpl_id.product_tmpl_ids
            )

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.onchange("product_uom_id")
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_id:
            return res
        if self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            self.product_uom_id = self.product_id.uom_id.id
            res["warning"] = {
                "title": _("Warning"),
                "message": _(
                    "The Product Unit of Measure you chose has"
                    " a different category than in the product form."
                ),
            }
        return res

    _sql_constraints = {
        (
            "product_tmpl_id_product_id_unique",
            "UNIQUE(product_tmpl_id,product_id)",
            "Option must be unique by configurable product",
        )
    }

    def toggle_active(self):
        raise UserError(
            _(
                "You can not active/inactive option manually,"
                "instead active/inactive related product"
            )
        )
