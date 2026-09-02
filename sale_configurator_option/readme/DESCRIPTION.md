This module extends the `sale_configurator_base` functionality to let the
customer choose **options** for a configurable product.

An option is a child line of the configurable product (parent) line. Options
are mostly services, e.g. the customer buying T-shirts can add a *flocking*
service on each T-shirt.

The **quantity** of an option can be:

- **proportional**: it follows the quantity of the parent line (`option_qty`
  times the parent quantity). For example 1 flocking for 1 T-shirt: 50
  T-shirts → 50 flockings;
- **independent**: the quantity is fixed, whatever the parent quantity. For
  example a setup service charged once per order.

The **price**: each option line is priced with its own product and pricelist
rules (quantity discounts are computed on the option's own quantity). The
prices of the options are added to the price of the parent line in the
configurable subtotal.

The **delivered quantities**: only the parent line is delivered. Options
(services) have no stock moves; their delivered quantity simply follows the
delivered quantity of the parent line *in proportion*. This delivery behavior
is provided by `sale_stock_configurator_option`: without it, no delivery is
managed for the configurable products.

Example: the customer buys 50 T-shirts priced 10.00 each and 1 flocking at
15.00 on each. The flocking has a *proportional* quantity.

- T-shirt (parent): 50 × 10.00 = 500.00
- Flocking (option): 50 × 15.00 = 750.00
- Configurable total: 1250.00

Only the 50 T-shirts are delivered; 1250.00 are invoiced.

If the flocking had an *independent* quantity, its quantity would be fixed
(e.g. 1 flocking charged once whatever the number of T-shirts).

The options proposed for a configurable product can be marked as *default*
ones: they are then automatically added when the configurable product is
selected.