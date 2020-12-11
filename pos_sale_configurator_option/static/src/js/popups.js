odoo.define("pos_sale_configurator_option.views", function (require) {
    /* Views related stuff */
    var screens = require("point_of_sale.screens");
    var PopUpWidget = require("point_of_sale.popups");
    var chrome = require("point_of_sale.chrome");
    var gui = require("point_of_sale.gui");
    var ppt = require("pos_product_template.pos_product_template");
    var core = require("web.core");
    var QWeb = core.qweb;

    chrome.Chrome.include({
        build_widgets: function () {
            // Create popup, add it to dom and hide it
            this._super();
            this.select_option = new SelectConfigOptionPopupWidget(this, {});
            this.select_option.appendTo($(this.$el));
            // Hide the popup because all pop up are displayed at the
            // beginning by default
            this.select_option.hide();
        },
    });

    var SelectConfigOptionPopupWidget = PopUpWidget.extend({
        template: "SelectConfigOptionPopupWidget",
        init: function (parent, args) {
            this._super(parent, args);
            this.events["click button.up"] = "change_qty";
            this.events["click button.down"] = "change_qty";
            this.events["blur input.quantity"] = "change_qty";
        },
        change_qty: function (evt) {
            var clicked_input = evt.target;
            var line = clicked_input.closest("tr");
            var output_qty = line.querySelector("input.quantity");
            var delta = parseInt(
                clicked_input.dataset.delta ||
                    clicked_input.parentElement.dataset.delta,
                10
            ); // Clicked_input can be "+" or "button"
            delta = delta ? delta : 0;
            output_qty.value = Math.max(
                parseInt(output_qty.dataset.min, 10),
                Math.min(
                    parseInt(output_qty.value, 10) + delta,
                    parseInt(output_qty.dataset.max, 10)
                ) // Limit input to max_qty
            ); // No negative qty
            // TODO: support float qty
            return false;
        },
        show: function (options) {
            var options = options || {};
            // Following fields are used in xml
            this.product = options.product;
            this.config_options = options.config_options;
            this.selected_options = options.selected_options || [];
            this.pricelist = options.pricelist;

            this._super(options);

            this.selected_options.forEach(function (option) {
                // Prefill with saved values
                var id = option.id;
                var selector = 'tr.element[data-config_option_id="' + id + '"]';
                var element = this.el.querySelector(selector);
                if (element) {
                    var input_quantity = element.querySelector("input.quantity");
                    input_quantity.value = parseInt(option.quantity, 10);
                    var input_notes = element.querySelector("textarea.notes");
                    input_notes.value = option.notes;
                }
            }, this);
        },
        click_confirm: function () {
            var selected_options = [];
            var orderline;
            var self = this;
            var lines = self.el.querySelectorAll("tr.element");
            lines.forEach(function (line) {
                var config_id = line.dataset.config_option_id;
                var input_quantity = line.querySelector("input.quantity");
                var qty = parseInt(input_quantity.value, 0);
                if (qty > 0) {
                    var notes = line.querySelector("textarea.notes").value;
                    var description = line.querySelector("td.description").innerText;
                    var price = parseFloat(line.querySelector("td.price").innerText);
                    var product_id = line.dataset.product_id;
                    selected_options.push({
                        id: config_id,
                        product_id: product_id,
                        description: description,
                        quantity: qty,
                        price: price,
                        notes: notes,
                    });
                }
            });

            this._super(); // TODO: utiliser this.option.confirm
            order = self.pos.get("selectedOrder");
            if (this.options.configure_line_id) {
                // Update product
                orderline = order.orderlines._byId[this.options.configure_line_id];
            } else {
                var product = jQuery.extend(true, {}, self.product);
                // Product.selected_options = selected_options;
                order.add_product(product);
                orderline = order.get_selected_orderline();
            }
            orderline.selected_options = selected_options;
            orderline.set_selected(); // Refresh pane
            orderline.set_quantity(orderline.quantity); // Refresh price
        },
    });
    gui.define_popup({
        name: "select-config-option",
        widget: SelectConfigOptionPopupWidget,
    });

    screens.OrderWidget.include({
        // Add the "configure" button on products in the cart
        render_orderline: function (orderline) {
            self = this;
            var template = "Orderline";
            if (!_.isUndefined(orderline.selected_options)) {
                template += "WithConfigOptions";
            }
            var el_str = QWeb.render(template, {widget: this, line: orderline});
            var el_node = document.createElement("div");
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            el_node.orderline = orderline;
            el_node.addEventListener("click", this.line_click_handler);
            $(el_node)
                .find("button")
                .on("click", function () {
                    var product = orderline.product;
                    var options = self.pos.db.get_options(product.id);
                    var params = {
                        product: product,
                        config_options: options,
                        orderline: orderline,
                        configure_line_id: orderline.id,
                        pricelist: orderline.order.pricelist,
                        selected_options: orderline.selected_options,
                    };
                    self.gui.show_popup("select-config-option", params);
                });
            orderline.node = el_node;
            return el_node;
        },
    });

    ppt.VariantListWidget.include({
        /* On click on a variant */
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.click_variant_handler_original = this.click_variant_handler;
            this.click_variant_handler = function (event) {
                var product_id = this.dataset.variantId;
                var product = self.pos.db.get_product_by_id(product_id);
                var order = self.pos.get("selectedOrder");
                var last_orderline = order.pos
                    .get("selectedOrder")
                    .get_last_orderline();

                // Chain operations screen
                // todo refactor with product scree widget
                var options = self.pos.db.get_options(product.id);
                if (options.length > 0) {
                    var params = {
                        product: product,
                        config_options: options,
                        pricelist: self._get_active_pricelist(),
                        configure_line_id: false,
                        selected_operations: [],
                    };
                    self.gui.show_popup("select-config-option", params);
                } else {
                    self.click_variant_handler_original.call(this, event);
                }
            };
        },
        _get_active_pricelist: function () {
            // Todo refactor with product scree widget
            var current_order = this.pos.get_order();
            var current_pricelist = this.pos.default_pricelist;

            if (current_order) {
                current_pricelist = current_order.pricelist;
            }

            return current_pricelist;
        },
    });

    screens.ProductScreenWidget.include({
        click_product: function (product) {
            // On click on a template
            var options = this.pos.db.get_options(product.id);
            if (product.product_variant_count == 1 && options.length > 0) {
                var params = {
                    product: product,
                    config_options: options,
                    pricelist: this._get_active_pricelist(),
                    configure_line_id: false,
                    selected_operations: [],
                };
                this.gui.show_popup("select-config-option", params);
            } else {
                this._super(product);
            }
        },
        _get_active_pricelist: function () {
            var current_order = this.pos.get_order();
            var current_pricelist = this.pos.default_pricelist;

            if (current_order) {
                current_pricelist = current_order.pricelist;
            }

            return current_pricelist;
        },
    });
});
