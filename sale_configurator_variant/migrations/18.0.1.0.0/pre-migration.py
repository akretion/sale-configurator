# Copyright 2025 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Renaming field is_multi_variant_line")
    openupgrade.rename_fields(
        env,
        [
            (
                "sale.order.line",
                "sale_order_line",
                "is_multi_variant_line",
                "is_configurable_with_variant",
            ),
        ],
    )
