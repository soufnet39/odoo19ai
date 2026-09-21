/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Registry for landing page apps.
 * Each module registers its apps via:
 *   registry.category("shakliyat_landing_apps").add("key", { name, icon, action, ... })
 *
 * The `action` can be either:
 *   - An action XML ID (e.g. "sale.action_orders") — opened via doAction()
 *   - A path string (e.g. "/odoo/orders") — navigated to via window.location
 */
const landingApps = registry.category("shakliyat_landing_apps");

export class LandingPage extends Component {
    setup() {
        this.actionService = useService("action");
        this.apps = landingApps.getAll().map((val) => ({ ...val }));
    }

    onAppClick(app) {
        if (app.path) {
            // Direct navigation via window.location (clean URL)
            window.location.href = app.path;
        } else if (app.action) {
            this.actionService.doAction(app.action);
        }
    }
}

LandingPage.template = "shakliyat.LandingPage";

// Register the client action
registry.category("actions").add("shakliyat.landing_page", LandingPage);
