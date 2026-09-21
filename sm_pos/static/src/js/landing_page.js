/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_pos", {
    name: "Comptoire SM",
    description: "Point de vente",
    icon: "fa-cash-register",
    color: "#00695C",
    action: "sm_pos.action_sm_pos",
});