/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    var _super_order = models.Orderline.prototype;
    // Include not available
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_order.initialize.call(this, attr, options);
            this.selected_options = this.selected_options || [];
        },
        compute_fixed_price: function (price) {
            // Compute fixed priced is call once
            // set_unit_price is call twice
            price += this.get_options_price();
            return _super_order.compute_fixed_price.apply(this, arguments);
        },
        get_options_price: function () {
            // Sum the price of selected options
            var operation_price = 0;
            if (this.selected_options) {
                this.selected_options.forEach(function (option) {
                    operation_price += option.qty * option.price;
                });
            }
            return operation_price;
        },

        can_be_merged_with: function (orderline) {
            if (this.selected_options) return false;
            return _super_order.can_be_merged_with.call(this, orderline);
        },

        export_as_JSON: function () {
            var res = _super_order.export_as_JSON.call(this);
            if (this.selected_options) {
                res.config = {};
                res.config.selected_options = this.selected_options;
            }
            return res;
        },
        init_from_JSON: function () {
            // Rebuilt operations from JSON
            _super_order.init_from_JSON.apply(this, arguments);
            var json = arguments[0];
            if (json.config) {
                this.selected_options = json.config.selected_options;
                this.selected_options.forEach((option) => {
                    // Option.product is a proxy object and not wel
                    // serialized in json, better load it from id
                    option.product = this.pos.db.get_product_by_id(option.product_id);
                });
            }
        },
    });

    models.PosModel.prototype.models.some(function (model) {
        if (model.model !== "product.product") {
            return false;
        }
        // Add name and attribute_value_ids to list of fields
        // to fetch for product.product
        ["sale_alone_forbidden", "is_option", "configurable_option_ids"].forEach(
            function (field) {
                if (model.fields.indexOf(field) === -1) {
                    model.fields.push(field);
                }
            }
        );
        return true; // Exit early the iteration of this.models
    });
    models.load_models([
        {
            model: "product.configurator.option",
            fields: [
                "product_id",
                "product_uom_id",
                "sequence",
                "option_qty_type",
                // From sale_configurator_option_restricted_qty
                "sale_min_qty",
                "sale_max_qty",
            ],
            loaded: function (self, config_options) {
                // Create a lookup by id
                var options = {};
                config_options.forEach(function (opt) {
                    options[opt.id] = opt;
                });
                self.db.config_options = options;
            },
        },
    ]);
    return;
});
