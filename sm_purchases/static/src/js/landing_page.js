/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_purchases", {
    name: "Achats SM",
    description: "Gestion des achats",
    icon: "fa-cart-plus",
    color: "#2E7D32",
    action: "sm_purchases.action_sm_purchases_purchase",
});