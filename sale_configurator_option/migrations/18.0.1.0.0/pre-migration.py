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
                "product_conf_tmpl_id",
                "configurator_id",
            ),
            (
                "product.configurator.option",
                "product_configurator_option",
                "option_product_tmpl_id",
                "product_tmpl_id",
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
            (
                "product.template",
                "product_template",
                "count_used_on_option_line",
                "count_used_in_options",
            ),
            # ProductProduct
            (
                "product.product",
                "product_product",
                "used_on_product_tmpl_ids",
                "used_in_configurable_product_tmpl_ids",
            ),
            (
                "product.product",
                "product_product",
                "used_on_product_ids",
                "used_in_configurable_product_ids",
            ),
            (
                "product.product",
                "product_product",
                "used_on_option_line_ids",
                "used_as_option_ids",
            ),
            # SaleOrderLine
            (
                "sale.order.line",
                "sale_order_line",
                "option_ids",
                "child_option_ids",
            ),
            (
                "sale.order.line",
                "sale_order_line",
                "option_unit_qty",
                "option_qty",
            ),
            (
                "sale.order.line",
                "sale_order_line",
                "product_option_id",
                "option_id",
            ),
        ],
    )
