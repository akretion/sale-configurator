/* Copyright 2025 Akretion
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {
    get productName() {
        const isConfigurableWithVariant =
            this.props.record.data.is_configurable_with_variant;
        const productTemplateData = this.props.record.data.product_template_id;

        if (
            isConfigurableWithVariant &&
            productTemplateData &&
            productTemplateData[1]
        ) {
            return productTemplateData[1];
        }

        return super.productName;
    },
});
