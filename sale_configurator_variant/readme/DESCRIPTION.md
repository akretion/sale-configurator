This module extends the `sale_configurator_base` functionality for products
that are sold in **several variants** (e.g. different colors or sizes of a
given model), when the customer wants to mix the quantities of the variants on
a single Sale Order.

When the line is configurable *with variants*:

- the **parent line** represents the product itself: it has **no price of its
  own** (`price_unit == 0`) and its quantity is the **sum of the quantities of
  all its variants**;
- each **variant** is a child line with its own product, quantity and price.

The **prices of the variants are based on the total quantity of the parent
line** (the sum of the quantities of all the variants), not on each variant
quantity separately. This way, quantity-based discount rules of the pricelists
are applied on the *cumulated* quantity of all the variants: buy the total over
a threshold in several variants, and the discount applies anyway.

The **delivered quantities**: each variant line is a real product for which a
stock move is generated with its own quantity; the delivery quantity is tracked
through the *parent* line.

Example: T-shirts priced 10.00 each with a 20% quantity discount above 40
T-shirts. The customer buys 50 T-shirts: 30 in size M and 20 in size L.

- T-shirt (parent): quantity 50, price 0.00
- T-shirt size M (variant): 30 × 8.00 = 240.00
- T-shirt size L (variant): 20 × 8.00 = 160.00
- Configurable total: 400.00

The 20% discount is applied on the parent's total quantity (50 T-shirts
is above the 40 threshold) and each variant is priced 8.00 (10.00 -
20%).

This usage is complementary to `sale_configurator_option`: a configurable
product *with variants* can also have **options**, whose proportional quantity
is computed from the parent line quantity (the sum of the variants). For
example, a single *flocking* option is applied on the whole set of sizes.