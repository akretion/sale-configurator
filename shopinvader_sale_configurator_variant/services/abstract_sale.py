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

    def _convert_one_line(self, line):
        res = super()._convert_one_line(line)
        res["variants"] = []
        for vline in line.variant_ids:
            res["variants"].append(super()._convert_one_line(vline))
        return res
