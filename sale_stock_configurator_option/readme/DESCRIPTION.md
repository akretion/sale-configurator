This module glues `sale_configurator_option` with the **stock** application to
manage the delivery of configurable products.

The options (services, e.g. the flocking of a T-shirt) are **not delivered**:
no stock move is generated for them. Only the configurable products (the
parent lines and the other real products) appear in the picking.

The delivered quantity of an option is computed *proportionally* to the
delivered quantity of its parent line: for example, if the picking only
delivers half of the T-shirts, the flocking option is considered as delivered
for half of its quantity too. This keeps the invoicing based on the delivered
quantities consistent.

Example: a picking delivers 25 of the 50 ordered T-shirts.

- T-shirt (parent): 25 delivered
- Flocking (option): 25 delivered (proportional to the T-shirt's delivered
  quantity, although no flocking stock move exists)