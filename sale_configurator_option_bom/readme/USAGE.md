1. Create a Manufacturable and Configurable product
    - Create a new configurable product with a Make To Order route
    - Add an Option with "Independent Qty" as "Option Qty Type"
    - Add a BoM to manufacture this product, with a component line of quantity 3
    - In the field "Related Option" of the BoM's first component, choose the newly created Option

2. Create a Sale Order to sell this product
    - Create a Sale Order
    - Select the newly created Configurable Product and his Option
    - Set the Configurable Product's quantity to 4 and the Option's quantity to 2

3. Confirm the Sale Order to consume the related components
    - Confirm the Sale Order
    - Check the related Manufacture Order
    - The Component's consumed quantity will be 3\*2 = 6


## Exemple

If your configurable product is a "boots checkup" associated to an option service "changing shoelaces", you want to consume 2 shoelaces each time the option service is sold, and not each time the "boots checkup is sold".