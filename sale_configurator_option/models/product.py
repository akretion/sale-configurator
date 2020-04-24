# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons import decimal_precision as dp


class ProductConfiguratorOption(models.Model):
    _name = "product.configurator.option"
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = "Product Configurator Option"

    def _get_default_product_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order="id").id

    product_tmpl_id = fields.Many2one(
        "product.template",
        "Parent Product Template",
        auto_join=True,
        index=True,
        ondelete="cascade",
        required=True,
    )
    product_id = fields.Many2one("product.product", "Option", required=True)
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Product Unit of Measure",
        default=_get_default_product_uom_id,
        oldname="product_uom",
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement"
        " for the inventory control",
    )
    sequence = fields.Integer(
        "Sequence", default=1, help="Gives the sequence order when displaying."
    )
    opt_min_qty = fields.Float(
        string="Min Qty", default=0, digits=dp.get_precision("Product Unit of Measure")
    )
    opt_default_qty = fields.Float(
        string="Default Qty",
        oldname="default_qty",
        default=0,
        digits=dp.get_precision("Product Unit of Measure"),
        help="This is the default quantity set to the sale line option ",
    )
    opt_max_qty = fields.Float(
        string="Max Qty",
        oldname="max_qty",
        default=1,
        digits=dp.get_precision("Product Unit of Measure"),
        help="High limit authorised in the sale line option",
    )
    option_qty_type = fields.Selection(
        [
            ("proportional_qty", "Proportional Qty"),
            ("independent_qty", "Independent Qty"),
        ],
        string="Option qty Type",
        default="proportional_qty",
        required=True,
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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_configurable_opt = fields.Boolean(
        "Is a Configurable Product ?",
        help="Chek this, if the product is configurable with options",
    )
    configurable_option_ids = fields.One2many(
        "product.configurator.option",
        "product_tmpl_id",
        "Configurable Option Lines",
        copy=True,
    )
