import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-akretion-sale-configurator",
    description="Meta package for akretion-sale-configurator Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-pim_sale_configurator',
        'odoo12-addon-sale_configurator_base',
        'odoo12-addon-sale_configurator_option',
        'odoo12-addon-sale_configurator_option_area',
        'odoo12-addon-sale_configurator_option_link',
        'odoo12-addon-sale_configurator_option_restricted_qty',
        'odoo12-addon-sale_configurator_variant',
        'odoo12-addon-sale_stock_configurator_option',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
