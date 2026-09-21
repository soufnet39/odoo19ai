/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OrderLine extends Component {
    static template = "sm_pos.OrderLine";
    static props = {
        line: Object,
    };

    setup() {
        this.pos = useService("pos");
    }

    get total() {
        return this.props.line.qty * this.props.line.unit_price;
    }
}