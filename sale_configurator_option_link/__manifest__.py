# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Option Link",
    "summary": (
        "Module to manage Link betwen Options"
        " (the choise off one option add anthor option)"
    ),
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_option"],
    "data": ["views/product_view.xml"],
    "qweb": [],
}
