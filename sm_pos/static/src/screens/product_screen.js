/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ProductCard } from "../components/product_card";
import { OrderLine } from "../components/order_line";

export class ProductScreen extends Component {
    static template = "sm_pos.ProductScreen";
    static components = { ProductCard, OrderLine };
    static props = {
        onPay: Function,
        onReadyToClose: Function,
    };

    setup() {
        this.pos = useService("pos");
        this.state = useState({
            selectedCategoryId: false,
            searchTerm: "",
        });
    }

    get categories() {
        return this.pos.categories;
    }

    get products() {
        let products = this.pos.products;
        if (this.state.selectedCategoryId) {
            products = products.filter((p) => p.categ_id === this.state.selectedCategoryId);
        }
        if (this.state.searchTerm) {
            const term = this.state.searchTerm.toLowerCase();
            products = products.filter(
                (p) =>
                    p.name.toLowerCase().includes(term) ||
                    (p.code || "").toLowerCase().includes(term)
            );
        }
        return products;
    }

    get order() {
        return this.pos.order;
    }

    get orderTotal() {
        return this.pos.getOrderTotal();
    }

    selectCategory(categoryId) {
        this.state.selectedCategoryId =
            this.state.selectedCategoryId === categoryId ? false : categoryId;
    }

    pay() {
        this.props.onPay();
    }

    readyToClose() {
        this.props.onReadyToClose();
    }
}