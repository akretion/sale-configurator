odoo.define('pos_sale_configurator_option.main', function (require) {

    require("pos_sale_configurator_option.db_and_model");

    var models = require('point_of_sale.models');


    var _super_order = models.Orderline.prototype;
    //include not available
    models.Orderline = models.Orderline.extend({
        compute_fixed_price: function(price){
            // compute fixed priced is call once
            // set_unit_price is call twice 
            price += this.get_options_price();
            return _super_order.compute_fixed_price.apply(this, arguments); 
        },
        get_options_price: function(){
            //sum the price of selected options
            var operation_price = 0;
            if (this.selected_options) {
                this.selected_options.forEach(function (option) {
                    operation_price += option.quantity * option.price;
                });
            }
            return operation_price;
        },

        can_be_merged_with: function(orderline){
            if (this.selected_options)
                return false;
            return _super_order.can_be_merged_with.call(this, orderline);
        },

        export_as_JSON: function() {
            var res = _super_order.export_as_JSON.call(this);
            if (this.selected_options) {
                res.config = {};
                res.config.selected_options = this.selected_options;
            }
            return res;
        },
        init_from_JSON: function() {
            // rebuilt operations from JSON
            _super_order.init_from_JSON.apply(this, arguments);
            var json = arguments[0];
            if (json.config) {
                this.selected_options = json.config.selected_options;
            }
        },
    });
});
