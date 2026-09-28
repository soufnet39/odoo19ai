/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

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
        this.searchInputRef = useRef("searchInput");
        this.state = useState({
            searchQuery: "",
        });

        this.rawApps = landingApps.getAll().map((val) => ({ ...val }));

        // Handle Cmd+K / Ctrl+K keyboard shortcut
        this._onKeyDown = (ev) => {
            if ((ev.metaKey || ev.ctrlKey) && ev.key.toLowerCase() === "k") {
                ev.preventDefault();
                this.focusSearch();
            }
        };

        onMounted(() => {
            window.addEventListener("keydown", this._onKeyDown);
        });

        onWillUnmount(() => {
            window.removeEventListener("keydown", this._onKeyDown);
        });
    }

    get userName() {
        const full = session.name || session.partner_display_name || "Smail";
        return full.split(" ")[0];
    }

    get greeting() {
        const hour = new Date().getHours();
        if (hour >= 5 && hour < 12) return "Bonjour";
        if (hour >= 12 && hour < 18) return "Bon après-midi";
        return "Bonsoir";
    }

    get formattedDate() {
        const options = { weekday: "long", day: "numeric", month: "long", year: "numeric" };
        const dateStr = new Date().toLocaleDateString("fr-FR", options);
        return dateStr.charAt(0).toUpperCase() + dateStr.slice(1);
    }

    get filteredApps() {
        const q = (this.state.searchQuery || "").trim().toLowerCase();
        if (!q) {
            return this.rawApps;
        }
        return this.rawApps.filter((app) => {
            const name = (app.name || "").toLowerCase();
            const desc = (app.description || "").toLowerCase();
            return name.includes(q) || desc.includes(q);
        });
    }

    onSearchInput(ev) {
        this.state.searchQuery = ev.target.value;
    }

    onSearchKeydown(ev) {
        if (ev.key === "Escape") {
            this.state.searchQuery = "";
            this.searchInputRef.el?.blur();
        } else if (ev.key === "Enter" && this.filteredApps.length === 1) {
            this.onAppClick(this.filteredApps[0]);
        }
    }

    focusSearch() {
        this.searchInputRef.el?.focus();
        this.searchInputRef.el?.select();
    }

    clearSearch() {
        this.state.searchQuery = "";
        this.focusSearch();
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
