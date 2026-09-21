/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class SessionScreen extends Component {
    static template = "sm_pos.SessionScreen";

    setup() {
        this.pos = useService("pos");
        this.orm = useService("orm");
        this.state = useState({
            configs: [],
            selectedConfigId: false,
            openingCash: 0,
            loading: false,
            error: false,
        });
        this._loadConfigs();
    }

    async _loadConfigs() {
        const configs = await this.orm.searchRead(
            "sm_pos.config",
            [["active", "=", true]],
            ["id", "name"]
        );
        this.state.configs = configs;
        if (configs.length) {
            this.state.selectedConfigId = configs[0].id;
        }
    }

    async openSession() {
        if (!this.state.selectedConfigId) {
            this.state.error = "Please select a Point of Sale.";
            return;
        }
        this.state.loading = true;
        this.state.error = false;
        try {
            await this.pos.openSession(this.state.selectedConfigId, this.state.openingCash);
            this.props.onSessionOpened();
        } catch (err) {
            this.state.error = err.message || "Failed to open session.";
        } finally {
            this.state.loading = false;
        }
    }
}