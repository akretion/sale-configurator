/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.db_and_model", function (require) {
    "use strict";
    var PosDB = require("point_of_sale.DB");

    PosDB.include({
        get_options: function (product_id) {
            var product = this.get_product_by_id(product_id);
            if (!product || !product.configurable_option_ids) {
                return [];
            }
            return product.configurable_option_ids.map(function (config_option_id) {
                return this.get_config_option(config_option_id);
            }, this);
        },
        get_config_option: function (config_option_id) {
            var config_option = this.config_options[config_option_id];
            return {
                id: config_option_id,
                product: this.get_product_by_id(config_option.product_id[0]),
                product_id: config_option.product_id[0],
                product_uom_id: config_option.product_uom_id,
                sale_min_qty: config_option.sale_min_qty,
                sale_max_qty: config_option.sale_max_qty,
                sale_default_qty: 0,
            };
        },
    });
});
