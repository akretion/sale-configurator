odoo.define("pos_sale_configurator_option.db_and_model", function (require) {
    var models = require("point_of_sale.models");
    var PosDB = require("point_of_sale.DB");
    var screens = require("point_of_sale.screens");
    var config_options = [];
    screens.ProductListWidget.include({
        set_product_list: function (product_list) {
            // Remove products which are option only
            var products_without_operations = [];
            var products_without_operations = product_list.filter(function (product) {
                return !product.sale_alone_forbidden;
            });
            return this._super(products_without_operations);
        },
    });

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
                // Todo necessaire  d'avoir product ?
                product_uom_id: config_option.product_uom_id,
                sale_default_qty: config_option.sale_default_qty,
                sale_min_qty: config_option.sale_min_qty,
                sale_max_qty: config_option.sale_max_qty,
            };
        },
    });

    models.PosModel.prototype.models.some(function (model) {
        if (model.model !== "product.product") {
            // Template ?
            return false;
        }
        // Add name and attribute_value_ids to list of fields
        // to fetch for product.product
        ["sale_alone_forbidden", "is_option", "configurable_option_ids"].forEach(
            function (field) {
                if (model.fields.indexOf(field) == -1) {
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
                "sale_default_qty",
                "option_qty_type",
                // From sale_configurator_option_restricted_qty
                "sale_min_qty",
                "sale_max_qty",
            ],
            loaded: function (self, config_options) {
                // Create a lookup by id
                options = {};
                config_options.forEach(function (opt) {
                    options[opt.id] = opt;
                });
                self.db.config_options = options;
                console.log("options loaded dans self: ", options, self);
            },
        },
    ]);
});
