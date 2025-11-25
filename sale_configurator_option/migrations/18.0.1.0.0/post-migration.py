import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info(
        "Migrate Bool fields like `is_configurable` or `is_option` "
        "to selection field `config_type`"
    )

    table_name = "product_template"

    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table_name}
        SET config_type = 'configurable'
        WHERE is_configurable_opt IS TRUE
        """,
    )

    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table_name}
        SET config_type = 'option'
        WHERE is_option IS TRUE AND config_type IS NULL
        """,
    )
