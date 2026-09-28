/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_invoices", {
    name: "Factures SM",
    description: "Gestion des factures",
    icon: "fa-file-text",
    web_icon: "/sm_invoices/static/description/icon.png",
    color: "#D51C1B",
    action: "sm_invoices.action_sm_invoices_invoice",
});
