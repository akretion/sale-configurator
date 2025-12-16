/** @odoo-module **/

import { SaleOrderLineProductField } from "@sale/js/sale_product_field";
import { patch } from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {

    get productName() {
        const isMultiVariant = this.props.record.data.is_multi_variant_line;
        const productTemplateData = this.props.record.data.product_template_id;
        
        if (isMultiVariant && productTemplateData && productTemplateData[1]) {
                return productTemplateData[1];  
            }
        
        return super.productName;
    }
});