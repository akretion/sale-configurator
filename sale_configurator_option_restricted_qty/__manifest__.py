# Copyright 2020 Akretion (http://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Option Restricted Qty",
    "summary": "Manage Restricted Qty on Sale configurator",
    "version": "12.0.1.0.0",
    "category": "Sale",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_configurator_option", "sale_restricted_qty"],
    "data": [
        "views/product_configurator_template_view.xml",
        "views/product_template_view.xml",
        "views/sale_view.xml",
    ],
    # "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
    "qweb": [],
}
