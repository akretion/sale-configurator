/* Copyright (C) 2020-Today Akretion (https://www.akretion.com)
    @author Raphaël Reverdy (https://www.akretion.com)
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
*/

odoo.define("pos_sale_configurator_option.SelectConfigOptionPopup", function (require) {
    "use strict";

    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const {useState} = owl.hooks;

    class SelectConfigOptionPopup extends AbstractAwaitablePopup {
        constructor(parent, props) {
            super(parent, props);
            this.state = useState({product: props.product, config_options: []});
            var options = this.createOptions(props.product, props.selected_options);
            this.state.config_options = options;
        }
        createOptions(product, selected_options) {
            var selectedLookup = {};
            selected_options.forEach((option) => {
                selectedLookup[option.id] = option;
            });
            return this.env.pos.db.get_options(product.id).map((option) => {
                var candidate = selectedLookup[option.id] || {};
                var product = this.env.pos.db.get_product_by_id(option.product_id);
                if (!product) {
                    throw new Error(
                        `Config Product ${option.product_id} not available in pos.`
                    );
                }
                return {
                    // Copy what we want to edit in the view
                    id: option.id,
                    product: product,
                    price: this._get_product_price(product),
                    sale_min_qty: option.sale_min_qty,
                    sale_max_qty: option.sale_max_qty,
                    qty: candidate.qty || option.sale_default_qty,
                    notes: candidate.notes || "",
                    description: option.product.display_name,
                };
            });
        }
        _get_pricelist() {
            const current_order = this.env.pos.get_order();
            if (current_order) {
                return current_order.pricelist;
            }
            return this.env.pos.default_pricelist;
        }
        _get_product_price(product) {
            return product.get_price(this._get_pricelist(), 1);
        }
        decreaseQty(option, evt) {
            // Todo assurer le bornage
            option.qty = this._validateQty(option.qty - 1, option);
        }
        increaseQty(option, evt) {
            option.qty = this._validateQty(option.qty + 1, option);
        }
        _validateQty(new_qty, option) {
            var qty = this._limitQty(new_qty, option.sale_min_qty, option.sale_max_qty);
            option.qty = qty;
            return qty;
        }
        _limitQty(qty, min, max) {
            return Math.max(min, Math.min(max, qty));
        }
        getPayload() {
            var ret = this.state.config_options
                .filter((option) => {
                    var qty = this._validateQty(option.qty, option); // Validate again because
                    // if user enter some value, we can't detect it.
                    return qty > 0;
                })
                .map((option) => {
                    // Flatten and persist
                    return {
                        id: option.id,
                        price: option.price,
                        product_id: option.product.id,
                        product: option.product,
                        description: option.description,
                        qty: option.qty,
                        notes: option.notes,
                    };
                });
            return ret;
        }
    }

    SelectConfigOptionPopup.template = "SelectConfigOptionPopup";
    SelectConfigOptionPopup.defaultProps = {
        confirmText: "Ok",
        cancelText: "Cancel",
        body: "",
        selected_options: [],
    };

    Registries.Component.add(SelectConfigOptionPopup);

    return SelectConfigOptionPopup;
});
