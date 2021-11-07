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

    def _prepare_option(self, option):
        return {
            "id": option.product_option_id.id,
            "product": {"id": option.product_id.id, "name": option.product_id.name},
            "qty": option.option_unit_qty,
        }

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res["options"] = [self._prepare_option(option) for option in line.option_ids]
        return res
