/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_base", {
    name: "Base SM",
    description: "Données communes et partagées",
    icon: "fa-cubes",
    web_icon: "/sm_base/static/description/icon.png",
    color: "#D51C1B",
    action: "sm_base.sm_base_wilayates_action",
});
