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
            # ProductConfiguratorOption
            (
                "product.configurator.option",
                "product_configurator_option",
                "product_tmpl_id",
                "configurable_product_tmpl_id",
            ),
            (
                "product.configurator.option",
                "product_configurator_option",
                "product_id",
                "option_product_id",
            ),
            (
                "product.configurator.option",
                "product_configurator_option",
                "product_conf_tmpl_id",
                "configurator_id",
            ),
            (
                "product.configurator.option",
                "product_configurator_option",
                "used_on_product_tmpl_ids",
                "used_in_configurable_product_tmpl_ids",
            ),
            # ProductConfiguratorTemplate
            (
                "product.configurator.template",
                "product_configurator_template",
                "configurable_option_ids",
                "option_ids",
            ),
            (
                "product.configurator.template",
                "product_configurator_template",
                "product_tmpl_ids",
                "configurable_product_tmpl_ids",
            ),
            # ProductTemplate
            (
                "product.template",
                "product_template",
                "sale_alone_forbidden",
                "is_not_sold_alone",
            ),
            (
                "product.template",
                "product_template",
                "product_conf_tmpl_id",
                "configurator_id",
            ),
            (
                "product.template",
                "product_template",
                "local_configurable_option_ids",
                "specific_option_ids",
            ),
            (
                "product.template",
                "product_template",
                "configurable_option_ids",
                "option_ids",
            ),
            # ProductProduct
            (
                "product.product",
                "product_product",
                "used_on_product_tmpl_ids",
                "used_in_configurable_product_tmpl_ids",
            ),
        ],
    )
