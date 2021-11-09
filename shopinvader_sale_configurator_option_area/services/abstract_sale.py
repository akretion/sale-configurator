# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _prepare_option(self, option):
        res = super()._prepare_option(option)
        res["area"] = {
            "id": option.option_area_id.id,
            "name": option.option_area_id.name,
        }
        return res
