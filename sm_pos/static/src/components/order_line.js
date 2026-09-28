/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OrderLine extends Component {
    static template = "sm_pos.OrderLine";
    static props = {
        line: Object,
        isSelected: Boolean,
        onClick: Function,
    };

    setup() {
        this.pos = useService("pos");
    }

    get total() {
        return this.pos.getLineTotal(this.props.line);
    }

    get formattedUnitPrice() {
        return (this.props.line.unit_price || 0).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    get formattedTotal() {
        return this.total.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }
}