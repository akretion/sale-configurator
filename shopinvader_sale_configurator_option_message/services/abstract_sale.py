# Copyright 2021 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _prepare_option(self, data, option):
        res = super()._prepare_option(data, option)
        res.update({"message": option.option_message})
        return res
