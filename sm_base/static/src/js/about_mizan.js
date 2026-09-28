/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class AboutMizanPage extends Component {
    static template = "sm_base.AboutMizanPage";
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");
        this.notification = useService("notification");
        this.state = useState({
            copiedEmail: false,
            copiedPhone: false,
        });
    }

    goToDashboard() {
        this.actionService.doAction("shakliyat.action_landing_page");
    }

    openModule(actionXmlId) {
        if (actionXmlId) {
            this.actionService.doAction(actionXmlId);
        }
    }

    copyText(type, text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        }
        if (type === "email") {
            this.state.copiedEmail = true;
            setTimeout(() => (this.state.copiedEmail = false), 2500);
        } else if (type === "phone") {
            this.state.copiedPhone = true;
            setTimeout(() => (this.state.copiedPhone = false), 2500);
        }
        this.notification.add("Copié dans le presse-papier !", {
            type: "success",
        });
    }
}

registry.category("actions").add("sm_base.about_mizan", AboutMizanPage);
