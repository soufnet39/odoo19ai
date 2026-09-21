/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_stocks", {
    name: "SM Stocks",
    description: "Stock management",
    icon: "fa-warehouse",
    color: "#1565C0",
    action: "sm_stocks.sm_stocks_stock_movement_action",
});