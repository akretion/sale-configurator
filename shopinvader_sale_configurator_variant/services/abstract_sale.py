# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    # TODO duplicated with shopinvader_sale_configurator_option
    # maybe create an abstract module
    def _is_item(self, line):
        if line.parent_id:
            return False
        else:
            return super()._is_item(line)

    def _prepare_variant(self, variant):
        return {
            "product": {"id": variant.product_id.id, "name": variant.product_id.name},
            "qty": variant.product_uom_qty,
        }

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res["variants"] = [
            self._prepare_variant(variant) for variant in line.variant_ids
        ]
        return res
