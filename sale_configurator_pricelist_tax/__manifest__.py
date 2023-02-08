# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator pricelist tax",
    "summary": "Glue module between sale_configurator_base and sale_order_pricelist_tax",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "sale_configurator_base",
        "sale_order_pricelist_tax",
    ],
    "data": ["views/sale_view.xml"],
    "demo": [],
    "auto_install": True,
    "sequence": 10,
}
