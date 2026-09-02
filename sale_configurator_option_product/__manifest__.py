# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "sale configurator option product",
    "license": "AGPL-3",
    "summary": "Add physical option products to manufacturing orders",
    "category": "Uncategorized",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/sale-configurator",
    "version": "18.0.0.0.0",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "sale_configurator_option",
        # https://github.com/OCA/manufacture
        "mrp_sale_info",
    ],
    "data": [],
    "demo": [],
    "qweb": [],
}
