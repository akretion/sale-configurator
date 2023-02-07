
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/akretion/sale-configurator/actions/workflows/pre-commit.yml/badge.svg?branch=14)](https://github.com/akretion/sale-configurator/actions/workflows/pre-commit.yml?query=branch%3A14)
[![Build Status](https://github.com/akretion/sale-configurator/actions/workflows/test.yml/badge.svg?branch=14)](https://github.com/akretion/sale-configurator/actions/workflows/test.yml?query=branch%3A14)
[![codecov](https://codecov.io/gh/akretion/sale-configurator/branch/14/graph/badge.svg)](https://codecov.io/gh/akretion/sale-configurator)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Sale Configurator

Sale configurator

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[sale_configurator_base](sale_configurator_base/) | 14.0.1.0.0 |  | Base module for sale configurator
[sale_configurator_option](sale_configurator_option/) | 14.0.1.0.0 |  | Base module for sale configurator
[sale_configurator_option_area](sale_configurator_option_area/) | 14.0.1.0.0 |  | Module to manage Option Typologies
[sale_configurator_option_link](sale_configurator_option_link/) | 14.0.1.0.0 |  | Module to manage Link betwen Options (the choise off one option add anthor option)
[sale_configurator_option_no_orphan](sale_configurator_option_no_orphan/) | 14.0.1.0.0 |  | Remove ability to add options as standard sale order lines
[sale_configurator_option_restricted_qty](sale_configurator_option_restricted_qty/) | 14.0.1.0.0 |  | Manage Restricted Qty on Sale configurator
[sale_configurator_variant](sale_configurator_variant/) | 14.0.1.1.1 |  | Extend sale configurator to manage product variant
[sale_configurator_variant_restricted_qty](sale_configurator_variant_restricted_qty/) | 14.0.1.0.0 |  | Glue module for compatibility
[sale_stock_configurator_option](sale_stock_configurator_option/) | 14.0.1.0.0 |  | Sale Stock glue module for sale configurator
[test_sale_configurator_option_variant](test_sale_configurator_option_variant/) | 14.0.1.0.0 |  | Module for testing compatibility


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[pim_sale_configurator](pim_sale_configurator/) | 14.0.1.0.0 (unported) |  | Auto instalable module for better UX with PIM

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Akretion
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
