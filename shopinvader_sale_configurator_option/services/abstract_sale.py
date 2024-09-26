# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _is_item(self, line):
        if line.parent_id:
            return False
        else:
            return super()._is_item(line)

    def _prepare_option(self, data, option):
        res = {
            "name": option.name,
            "qty": option.option_unit_qty,
            "amount": {
                "price": option.price_unit,
                "untaxed": option.price_subtotal,
                "tax": option.price_tax,
                "total": option.price_total,
                "total_without_discount": option.price_total_no_discount,
            },
            "discount": {"rate": option.discount, "value": option.discount_total},
        }
        for product_option in data["product"]["options"]:
            if product_option["id"] == option.product_option_id.id:
                res["option"] = product_option
        return res

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        if not line.parent_id:
            # avoid adding this field when _convert_one_line is call on children line
            # like in shopinvader_sale_configurable_variant
            res["options"] = [
                self._prepare_option(res, option) for option in line.option_ids
            ]
            res["amount"].update(
                {
                    "price_config_total": line.price_config_total,
                    "price_config_untaxed": line.price_config_subtotal,
                }
            )
        return res
