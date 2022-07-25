# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import CommonOptionCase


class TestCreateOrder(CommonOptionCase):
    def test_create_sale(self):
        data = self._get_pos_data()
        self._add_option(data)
        sales = self._create_sale([data])
        self.assertEqual(len(sales), 1)
        sale = sales[0]
        self.assertEqual(len(sale.order_line), 6)
        # Note
        # we have 3 product with option the total price is
        # 3 * (5*10 + 3*20 + 4 * 30) = 690
        # For the two other normal product
        # 1*5 + 2*15 = 35
        # Except total : 725
        self.assertEqual(sale.amount_total, 725)
