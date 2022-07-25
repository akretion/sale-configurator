/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.Orderline", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const Orderline = require("point_of_sale.Orderline");

    var PSCOOrderline = (Orderline) =>
        class PSCOOrderline extends Orderline {
            async configure() {
                var ret = await this.showPopup("SelectConfigOptionPopup", {
                    product: this.props.line.product,
                    selected_options: this.props.line.selected_options,
                });
                if (ret.confirmed) {
                    this.props.line.selected_options = ret.payload;
                    // Refresh price
                    // force price recompute
                    this.props.line.order.set_pricelist(
                        this.props.line.order.pricelist
                    );
                }
            }
        };
    Registries.Component.extend(Orderline, PSCOOrderline);

    return PSCOOrderline;
});
