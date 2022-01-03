# Copyright 2021 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Sale Configurator Option Message",
    "summary": "Sale Configurator Option integration for Shopinvader",
    "version": "14.0.1.0.0",
    "category": "e-commerce",
    "website": "https://github.com/akretion/sale-configurator",
    "author": "Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_configurator_option_message",
        "shopinvader_sale_configurator_option",
    ],
    "data": [
        "data/ir_export_product.xml",
    ],
    "auto_install": True,
}
