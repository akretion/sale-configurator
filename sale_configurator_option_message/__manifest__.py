# Copyright 2021 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Option Message",
    "summary": "Module to manage Option Message",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_configurator_option"],
    "data": [
        "views/product_configurator_option_view.xml",
        "views/sale_view.xml",
    ],
    "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
}
