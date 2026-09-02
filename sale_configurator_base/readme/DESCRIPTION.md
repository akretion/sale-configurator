This module is the technical base for the Sale Configurator modules (such as
`sale_configurator_option` or `sale_configurator_variant`).

It organizes the sale by creating a **parent/child hierarchy between the Sale
Order lines**:

- the *parent* line is the main product of the sale order (e.g. a T-shirt);
- the *child* lines are the extra elements the customer chose to configure it
  (e.g. a flocking service, a size, ...).

**Only the parent line is delivered**, its quantity is the quantity to deliver.
The children only contribute to the price: the total price of a configurable
line (`price_config_subtotal` / `price_config_total`) is the sum of the price
of the parent plus the prices of all its children.

Example: a customer buys 10 T-shirts priced 15.00 each and 10 flocking
services priced 5.00 each.

- T-shirt (parent): 10 × 15.00 = 150.00
- Flocking (child): 10 × 5.00 = 50.00
- Configurable total: 200.00

Only the 10 T-shirts are delivered; the 200.00 are the amount invoiced.

The configuration is done in a dedicated configurator dialog, opened with
the *Add a configurable product* button of the order lines. The child lines
are ordered right after their parent line and are made read-only in the Sale
Order: they can only be edited through the configurator dialog.