/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_reports", {
    name: "SM Reports",
    description: "Rapports et analyses",
    icon: "fa-line-chart",
    web_icon: "/sm_reports/static/description/icon.png",
    color: "#D51C1B",
    action: "sm_reports.sm_reports_customer_sales_action",
});
