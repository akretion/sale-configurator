/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.ProductWidget", function (require) {
    "use strict";
    var Registries = require("point_of_sale.Registries");
    var ProductsWidget = require("point_of_sale.ProductsWidget");

    const PSCOProductsWidget = (ProductsWidget) => {
        class PSCOProductsWidget extends ProductsWidget {
            get productsToDisplay() {
                var ret = super.productsToDisplay.filter(
                    (product) => !product.sale_alone_forbidden
                );
                return ret;
            }
        }
        return PSCOProductsWidget;
    };

    Registries.Component.extend(ProductsWidget, PSCOProductsWidget);
    return PSCOProductsWidget;
});
