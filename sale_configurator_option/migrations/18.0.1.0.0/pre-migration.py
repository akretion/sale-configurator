# Copyright 2025 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    logger.info("Renaming fields in sale_configurator_option")
    openupgrade.rename_fields(
        env,
        [
            (
                "product.configurator.option",
                "product_configurator_option",
                "product_tmpl_id",
                "configurable_product_tmpl_id",
            ),
            (
                "product.template",
                "product_template",
                "sale_alone_forbidden",
                "is_not_sold_alone",
            ),
        ],
    )
