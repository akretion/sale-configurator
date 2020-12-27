/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.ProductScreen", function (require) {
    "use strict";
    var Registries = require("point_of_sale.Registries");
    var ProductScreen = require("point_of_sale.ProductScreen");

    const PSCOProductScreen = (ProductScreen) =>
        class PSCOProductScreen extends ProductScreen {
            async _clickProduct(event) {
                var product = event.detail;
                if (product.configurable_option_ids) {
                    return super._clickProduct(event);
                }
                var ret = await this.showPopup("SelectConfigOptionPopup", {
                    product: product,
                });
                if (ret.confirmed) {
                    super._clickProduct(event);
                    this._persistConfig(product, ret.payload);
                }
            }
            _persistConfig(product, new_config) {
                var line = this.currentOrder.get_selected_orderline();
                if (line.product.id !== product.id) {
                    // We are not editing the good orderline
                    // a previous add_product failed
                    // so we are editing the wrong line
                    console.log("orderline not good");
                    return;
                }
                line.selected_options = new_config;
                // Force price recompute
                line.order.set_pricelist(line.order.pricelist);
            }
        };

    Registries.Component.extend(ProductScreen, PSCOProductScreen);
});
