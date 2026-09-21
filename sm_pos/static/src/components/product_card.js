/** @odoo-module **/
import { Component } from "@odoo/owl";

export class ProductCard extends Component {
    static template = "sm_pos.ProductCard";
    static props = {
        product: Object,
        onClick: Function,
    };
}