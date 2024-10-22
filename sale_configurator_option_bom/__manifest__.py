# Copyright 2024 Akretion (http://www.akretion.com).
# @author Thomas BONNERUE <thomas.bonnerue@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale configurator option bom",
    "license": "AGPL-3",
    "summary": "add modification on sale product to have relation beetwin option \
    and bom",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "version": "14.0.1.0.0",
    "application": False,
    "installable": True,
    "depends": [
        "mrp",
        "sale_configurator_option",
        "mrp_sale_info",
    ],
    "data": [
        "views/mrp_bom_view.xml",
    ],
    "demo": [],
    "qweb": [],
}
