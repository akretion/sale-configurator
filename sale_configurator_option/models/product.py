# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp


class ProductConfiguratorOption(models.Model):
    _name = 'product.configurator.option'
    _order = "sequence, id"
    _rec_name = "product_config_id"
    _description = 'Product Configurator Option'

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        auto_join=True, index=True, ondelete="cascade", required=True)
    product_config_id = fields.Many2one(
        'product.product', 'Option', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id,
        oldname='product_uom', required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement"
        " for the inventory control")
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    opt_qty = fields.Float(
        'Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    opt_min_qty = fields.Float(
        string="Min Qty", default=0)
    opt_default_qty = fields.Float(
        string="Default Qty", oldname='default_qty', default=0,
        help="This is the default quantity set to the sale line option ")
    opt_max_qty = fields.Float(
        string="Max Qty", oldname='max_qty', default=1,
        help="High limit authorised in the sale line option")

    @api.onchange('product_config_id')
    def onchange_product_id(self):
        if self.product_config_id:
            self.product_uom_id = self.product_config_id.uom_id.id

    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_config_id:
            return res
        if self.product_uom_id.category_id !=\
                self.product_config_id.uom_id.category_id:
            self.product_uom_id = self.product_config_id.uom_id.id
            res['warning'] = {
                'title': _('Warning'),
                'message': _(
                    'The Product Unit of Measure you chose has'
                    ' a different category than in the product form.')
                }
        return res


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    configurable_opt_ok = fields.Boolean(
        'Has a Configurable Options?',
        help='Chek this, if the product has a configurable options',
    )
    product_config_opt_ids = fields.One2many(
        'product.configurator.option', 'product_tmpl_id',
        'Option Lines', copy=True)
