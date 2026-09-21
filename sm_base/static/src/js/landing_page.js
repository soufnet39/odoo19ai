/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_base", {
    name: "Base SM",
    description: "Données communes et partagées",
    icon: "fa-globe",
    color: "#714B67",
    action: "sm_base.sm_base_wilayates_action",
});
