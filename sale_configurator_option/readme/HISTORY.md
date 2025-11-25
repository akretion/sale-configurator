## 18.0.1.0.0 (2025-11-22)

* **[MIGRATION]** Migration to Odoo 18.0.
* **[BREAKING]** **Major field name refactoring** for model consistency. All fields listed below have been renamed. ([\#68](https://github.com/akretion/sale-configurator/pull/68)).

| Model | Old Field Name | New Field Name |
| :--- | :--- | :--- |
| **ProductConfiguratorOption** | `product_conf_tmpl_id` | `configurator_id` |
| | `product_tmpl_id` | `configurable_product_tmpl_id` |
| | `option_product_tmpl_id` | `product_tmpl_id` |
| | `used_on_product_tmpl_ids` | `used_in_configurable_product_tmpl_ids` |
| **ProductConfiguratorTemplate** | `configurable_option_ids` | `option_ids` |
| | `product_tmpl_ids` | `configurable_product_tmpl_ids` |
| **ProductTemplate** | `sale_alone_forbidden` | `is_not_sold_alone` |
| | `product_conf_tmpl_id` | `configurator_id` |
| | `local_configurable_option_ids` | `specific_option_ids` |
| | `configurable_option_ids` | `option_ids` |
| | `count_used_on_option_line` | `count_used_as_option` |
| **ProductProduct** | `used_on_product_tmpl_ids` | `used_in_configurable_product_tmpl_ids` |
| | `used_on_product_ids` | `used_in_configurable_product_ids` |
| | `used_on_option_line_ids` | `used_as_option_ids` |
| **SaleOrderLine** | `option_ids` | `child_option_ids` |
| | `option_unit_qty` | `option_qty` |
| | `product_option_id` | `option_id` |


Also, the following fields have been replaced by the single selection field `config_type`.

| Model | Replaced Fields |
| :--- | :--- |
| **ProductTemplate** | `is_configurable_opt`, `is_option` |
| **SaleOrderLine** | `child_type`, `is_configurable`, `is_configurable_opt` |