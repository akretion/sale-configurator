# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Variant Restricted Qty",
    "summary": "Glue module for compatibility",
    "version": "14.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_configurator_variant",
        "sale_restricted_qty",
    ],
    "data": [],
    "demo": [],
}
