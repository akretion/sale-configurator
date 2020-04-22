# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    parent_option_id = fields.Many2one("sale.order.line", "Parent Option")
    option_ids = fields.One2many(
        "sale.order.line", "parent_option_id", "Options")
    is_configurable_opt = fields.Boolean(
        'Is the product configurable Option ?',
        related="product_id.is_configurable_opt")
    pricelist_id = fields.Many2one(
        related='order_id.pricelist_id',
        string='Pricelist', store=True, readonly=True)
    option_unit_qty = fields.Float(
        string='Option Unit Qty',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.0)
    parent_option_qty = fields.Float(
        related="parent_option_id.product_uom_qty")
    force_option_qty = fields.Boolean(
        'Force Option Qty',
        )

    @api.multi
    def open_sale_line_config_option(self):
        self.ensure_one()
        view_id = self.env.ref(
            'sale_configurator_option.sale_order_line_config_option_view_form'
            ).id
        return {
            'name': _('Option Configurator'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self._name,
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'res_id': self.id,
            }

    @api.model
    def _get_price_config_subtotal(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, self)._get_price_config_subtotal()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            for opt in self.option_ids:
                res += opt.price_subtotal
        return res

    @api.model
    def _get_price_config_total(self):
        """
        get the config subtotal amounts of the SO line.
        """
        res = super(SaleOrderLine, self)._get_price_config_total()
        if self.parent_option_id:
            res = 0
        elif self.option_ids:
            for opt in self.option_ids:
                res += opt.price_total
        return res

    def _prepare_sale_line_option(self, opt):
        return {
            'order_id': self.order_id.id,
            'product_id': opt.product_id.id,
            'option_unit_qty': opt.opt_default_qty,
            'product_uom_qty':
            opt.opt_default_qty * self.product_uom_qty,
            'product_uom': opt.product_uom,
            }

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.option_ids = False
        if self.product_id.is_configurable_opt:
            options = []
            for opt in self.product_id.configurable_option_ids:
                if opt.opt_default_qty:
                    options.append(
                        (0, 0, self._prepare_sale_line_option(opt)))
            self.option_ids = options
        return res

    @api.onchange('product_uom',
        'option_unit_qty', 'parent_option_qty')
    def product_uom_change(self):
        if self.parent_option_id:
            self.product_uom_qty =\
                self.option_unit_qty * self.parent_option_qty
        res = super(SaleOrderLine, self).product_uom_change()
        return res
