/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Numpad } from "../components/numpad";

export class PaymentScreen extends Component {
    static template = "sm_pos.PaymentScreen";
    static components = { Numpad };

    setup() {
        this.pos = useService("pos");
        this.state = useState({
            selectedMode: null,
            amountInput: "",
            paying: false,
            error: false,
        });
    }

    get orderTotal() {
        return this.pos.getOrderTotal();
    }

    get paidTotal() {
        return this.pos.getPaidTotal();
    }

    get remaining() {
        return this.orderTotal - this.paidTotal;
    }

    get change() {
        const amount = parseFloat(this.state.amountInput) || 0;
        return amount - this.remaining;
    }

    selectMode(mode) {
        this.state.selectedMode = mode;
        this.state.amountInput = this.remaining.toFixed(2);
    }

    onInput(key) {
        if (key === "." && this.state.amountInput.includes(".")) return;
        this.state.amountInput += key;
    }

    onBackspace() {
        this.state.amountInput = this.state.amountInput.slice(0, -1);
    }

    onClear() {
        this.state.amountInput = "";
    }

    async pay() {
        if (!this.state.selectedMode) {
            this.state.error = "Please select a payment mode.";
            return;
        }
        const amount = parseFloat(this.state.amountInput) || 0;
        if (amount <= 0) {
            this.state.error = "Please enter a valid amount.";
            return;
        }
        this.state.paying = true;
        this.state.error = false;
        try {
            if (!this.pos.order.id) {
                await this.pos.syncOrder();
            }
            await this.pos.addPayment(this.state.selectedMode, amount);
            if (this.pos.getPaidTotal() >= this.orderTotal) {
                this.pos.newOrder();
                this.props.onPaymentDone();
            } else {
                this.state.amountInput = "";
                this.state.selectedMode = null;
            }
        } catch (err) {
            this.state.error = err.message || "Payment failed.";
        } finally {
            this.state.paying = false;
        }
    }

    back() {
        this.props.onBack();
    }
}