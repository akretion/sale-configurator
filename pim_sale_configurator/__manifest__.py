# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "PIM Sale Configurator",
    "summary": "Auto instalable module for better UX with PIM",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "auto_install": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale_configurator_base", "pim"],
    "data": ["views/menu.xml"],
    "demo": [],
    "qweb": [],
}
