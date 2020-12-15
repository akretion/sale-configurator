odoo.define('pos_sale_configurator_option.db_and_model', function (require) {

    var models = require('point_of_sale.models');
    var PosDB = require("point_of_sale.DB");
    var screens = require("point_of_sale.screens");
    var config_options = [];
    screens.ProductListWidget.include({
        set_product_list: function(product_list){
            //remove products which are option only
            var products_without_operations = [];
            var products_without_operations = product_list.filter(function (product) {
                return !product.sale_alone_forbidden;
            })
            return this._super(products_without_operations);
        },
    });

    PosDB.include({
        get_options: function(product_id) {
            var product = this.get_product_by_id(product_id);
            if (!product || !product.configurable_option_ids) {
                return [];
            }
            return product.configurable_option_ids.map(function(config_option_id) {
                return this.get_config_option(config_option_id);
            }, this);
        },
        get_config_option: function(config_option_id) {
            var config_option = this.config_options[config_option_id]
            return {
                'id': config_option_id,
                'product': this.get_product_by_id(config_option.product_id[0]),
                // todo necessaire  d'avoir product ?
                'product_uom_id': config_option.product_uom_id,
                'sale_default_qty': 0,
                'sale_min_qty': config_option.sale_min_qty,
                'sale_max_qty': config_option.sale_max_qty || 1000,
            }
        }
    });

    models.PosModel.prototype.models.some(function (model) {
        if (model.model !== 'product.product') { // template ?
            return false;
        }
        // add name and attribute_value_ids to list of fields
        // to fetch for product.product
        [
            'sale_alone_forbidden',
            'is_option',
            'configurable_option_ids',
        ].forEach(function (field) {
            if (model.fields.indexOf(field) == -1) {
                model.fields.push(field);
            }
        });
        return true; //exit early the iteration of this.models
    });
    models.load_models([{
        model: 'product.configurator.option',
        fields: [
            'product_id',
            'product_uom_id',
            'sequence',
            'option_qty_type',
            // from sale_configurator_option_restricted_qty
            'sale_min_qty',
            'sale_max_qty'
        ],
        loaded: function(self, config_options){
            //create a lookup by id
            options = {}
            config_options.forEach(function (opt) {
                options[opt.id] = opt;
            });
            self.db.config_options = options;
            console.log('options loaded dans self: ',options,  self);
        },
    }]);

});
