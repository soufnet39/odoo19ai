/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ProductCard extends Component {
    static template = "sm_pos.ProductCard";
    static props = {
        product: Object,
        onClick: Function,
    };

    setup() {
        this.pos = useService("pos");
    }

    get cartQty() {
        return this.pos.getProductQtyInCart(this.props.product.id);
    }

    get formattedPrice() {
        return (this.props.product.price || 0).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }
}