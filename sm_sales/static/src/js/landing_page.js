/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_sales", {
    name: "Ventes SM",
    description: "Gestion des ventes",
    icon: "fa-shopping-cart",
    web_icon: "/sm_sales/static/description/icon.png",
    color: "#D51C1B",
    action: "sm_sales.action_sm_sales_order",
});
