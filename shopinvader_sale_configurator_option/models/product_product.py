# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO price of option should have the same logic as the price on product
    # for now the code for computing the price is on the binding
    # option do not have binding
    # we need to refactor the base module
    # for now we have duplicated the code here

    shopinvader_price = fields.Serialized(
        compute="_compute_shopinvader_price", string="Shopinvader Price"
    )

    def _compute_shopinvader_price(self):
        for record in self:
            record.shopinvader_price = record._get_all_shopinvader_price()

    def _get_all_shopinvader_price(self):
        self.ensure_one()
        res = {}
        backend = self._context["shopinvader_backend"]
        pricelist = backend.pricelist_id
        default_role = backend.customer_default_role
        if pricelist:
            res[default_role] = self._get_shopinvader_price(
                pricelist, None, backend.company_id
            )
        return res

    def _get_shopinvader_price(self, pricelist, fposition, company=None):
        self.ensure_one()
        return self._get_shopinvader_price_per_qty(1, pricelist, fposition, company)

    def _get_shopinvader_price_per_qty(self, qty, pricelist, fposition, company=None):
        product_id = self
        taxes = product_id.taxes_id.sudo().filtered(
            lambda r: not company or r.company_id == company
        )
        # get the expeced tax to apply from the fiscal position
        tax_id = fposition.map_tax(taxes, product_id) if fposition else taxes
        tax_id = tax_id and tax_id[0]
        product = product_id.with_context(
            quantity=qty, pricelist=pricelist.id, fiscal_position=fposition
        )
        final_price, rule_id = pricelist.get_product_price_rule(
            product, qty or 1.0, None
        )
        tax_included = tax_id.price_include
        account_tax_obj = self.env["account.tax"]
        # fix tax on the price
        value = account_tax_obj._fix_tax_included_price_company(
            final_price, product.taxes_id, tax_id, company
        )
        res = {
            "value": value,
            "tax_included": tax_included,
            "original_value": value,
            "discount": 0.0,
        }
        if pricelist.discount_policy == "without_discount":
            sol = self.env["sale.order.line"]
            new_list_price, currency_id = sol._get_real_price_currency(
                product, rule_id, qty or 1.0, product.uom_id, pricelist.id
            )
            # fix tax on the real price
            new_list_price = account_tax_obj._fix_tax_included_price_company(
                new_list_price, product.taxes_id, tax_id, company
            )
            product_precision = self.env["decimal.precision"].precision_get(
                "Product Price"
            )
            if (
                float_compare(new_list_price, value, precision_digits=product_precision)
                == 0
            ):
                # Both prices are equals. Product is wihout discount, avoid
                # divide by 0 exception
                return res
            discount = (new_list_price - value) / new_list_price * 100
            # apply the right precision on discount
            dicount_precision = self.env["decimal.precision"].precision_get("Discount")
            discount = float_round(discount, dicount_precision)
            res.update({"original_value": new_list_price, "discount": discount})
        return res
