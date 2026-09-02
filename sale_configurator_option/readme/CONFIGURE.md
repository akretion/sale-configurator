## Configure product options

To offer options on the sale order lines, you must first define them on the
products, either directly on each configurable product or through a reusable
*product configurator template*.

### Create the option products

Create a product for each option (e.g. a *Flocking* service) and set its
*Configuration type* to *Option*.

### Link the options to a configurable product

On the configurable product (e.g. the T-shirt), in the *Configurator Options*
tab, you can:

- add *specific options* directly on the product;
- or select a *product configurator template* that already defines a set of
  options shared by several products.

For each option, set:

- the *quantity type*: *Proportional* (the option quantity follows the parent
  quantity) or *Independent* (the option has its own fixed quantity, computed
  from the `option_qty` value);
- whether it is a *default* option, i.e. automatically added when the
  configurable product is selected.