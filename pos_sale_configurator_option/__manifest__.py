# Copyright 2020 Akretion (https://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "POS Sale Configurator Option",
    "summary": "Sell configuration from the Point Of Sale",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "sale_configurator_option",
        "pos_product_template",
        # "sale_configurator_option_restricted_qty"
    ],
    "data": ["views/pos_sale_configurator_option.xml"],
    "demo": [],
    "qweb": [
        'static/src/xml/pos_sale_configurator_option.xml',
    ],
}
