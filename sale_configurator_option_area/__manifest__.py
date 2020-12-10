# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Option Typology",
    "summary": "Module to manage Option Typologies",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_option"],
    "data": [
        "views/product_view.xml",
        "views/product_configurator_option_view.xml",
        "views/sale_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
    "qweb": [],
}
