# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Shopinvader Sale Configurator Option",
    "summary": "Shopinvader Sale Configurator Option",
    "version": "14.0.1.0.0",
    "category": "Shopinvader",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "shopinvader_sale_configurator_option",
        "sale_configurator_option_area",
    ],
    "data": [
        "data/ir_export_product.xml",
    ],
    "demo": [],
}
