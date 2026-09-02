# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Sale Configurator Base",
    "summary": "Parent/child hierarchy for configurable products",
    "version": "18.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/sale-configurator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sale"],
    "data": [
        "views/sale_view.xml",
        "templates/sale_report_templates.xml",
        "templates/account_invoice_templates.xml",
    ],
    "assets": {
        "web.assets_backend": ["sale_configurator_base/static/src/scss/sale_order.scss"]
    },
    "demo": [],
    "qweb": [],
}
