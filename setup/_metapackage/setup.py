import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-akretion-sale-configurator",
    description="Meta package for akretion-sale-configurator Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-sale_configurator_base',
        'odoo14-addon-sale_configurator_option',
        'odoo14-addon-sale_configurator_option_area',
        'odoo14-addon-sale_configurator_option_bom',
        'odoo14-addon-sale_configurator_option_link',
        'odoo14-addon-sale_configurator_option_no_orphan',
        'odoo14-addon-sale_configurator_option_product',
        'odoo14-addon-sale_configurator_option_restricted_qty',
        'odoo14-addon-sale_configurator_pricelist_tax',
        'odoo14-addon-sale_configurator_variant',
        'odoo14-addon-sale_configurator_variant_restricted_qty',
        'odoo14-addon-sale_stock_configurator_option',
        'odoo14-addon-test_sale_configurator_option_variant',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
