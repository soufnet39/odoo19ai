/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { SessionScreen } from "../screens/session_screen";
import { ProductScreen } from "../screens/product_screen";
import { PaymentScreen } from "../screens/payment_screen";
import { ClosingScreen } from "../screens/closing_screen";

export class PosApp extends Component {
    static template = "sm_pos.PosApp";
    static components = { SessionScreen, ProductScreen, PaymentScreen, ClosingScreen };

    setup() {
        this.pos = useService("pos");
        this.state = useState({
            screen: "session",
        });
    }

    get currentScreen() {
        return this.state.screen;
    }

    onSessionOpened() {
        this.state.screen = "product";
    }

    onPay() {
        this.state.screen = "payment";
    }

    onPaymentDone() {
        this.state.screen = "product";
    }

    onBackToProduct() {
        this.state.screen = "product";
    }

    onReadyToClose() {
        this.state.screen = "closing";
    }

    onClosingDone() {
        this.state.screen = "session";
    }

    onClosingBack() {
        this.state.screen = "product";
    }
}

registry.category("actions").add("sm_pos.pos_app", PosApp);