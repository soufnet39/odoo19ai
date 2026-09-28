/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_purchases", {
    name: "Achats SM",
    description: "Gestion des achats",
    icon: "fa-cart-plus",
    web_icon: "/sm_purchases/static/description/icon.png",
    color: "#D51C1B",
    action: "sm_purchases.action_sm_purchases_purchase",
});