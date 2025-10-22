# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ShopinvaderVariant(models.Model):
    _inherit = "shopinvader.variant"

    def jsonify(self, parser, one=False):
        backend = self.backend_id
        backend.ensure_one()
        return super(
            ShopinvaderVariant, self.with_context(shopinvader_backend=backend)
        ).jsonify(parser, one=one)
