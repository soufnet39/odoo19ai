/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ClosingScreen extends Component {
    static template = "sm_pos.ClosingScreen";
    static props = {
        onClosingDone: Function,
        onClosingBack: Function,
    };

    setup() {
        this.pos = useService("pos");
        this.state = useState({
            countedCash: 0,
            notes: "",
            loading: true,
            error: false,
        });
        this._init();
    }

    async _init() {
        this.state.loading = true;
        this.state.error = false;
        try {
            const data = await this.pos.startClosingControl();
            this.state.countedCash = data.cash_register_balance_end;
        } catch (err) {
            this.state.error = err.message || "Failed to start closing control.";
        } finally {
            this.state.loading = false;
        }
    }

    get session() {
        return this.pos.session;
    }

    get difference() {
        return Number(this.state.countedCash) - Number(this.session.cash_register_balance_end);
    }

    async closeSession() {
        this.state.loading = true;
        this.state.error = false;
        try {
            await this.pos.closeSession(this.state.countedCash, this.state.notes);
            this.props.onClosingDone();
        } catch (err) {
            this.state.error = err.message || "Failed to close session.";
            this.state.loading = false;
        }
    }

    async back() {
        this.state.loading = true;
        this.state.error = false;
        try {
            await this.pos.resumeSession();
            this.props.onClosingBack();
        } catch (err) {
            this.state.error = err.message || "Failed to cancel closing.";
            this.state.loading = false;
        }
    }
}