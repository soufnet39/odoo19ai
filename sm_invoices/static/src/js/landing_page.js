/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_invoices", {
    name: "Factures SM",
    description: "Gestion des factures",
    icon: "fa-file-text",
    color: "#875A7B",
    action: "sm_invoices.action_sm_invoices_invoice",
});
