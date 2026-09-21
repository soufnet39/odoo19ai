/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("shakliyat_landing_apps").add("sm_boxes", {
    name: "Caisses SM",
    description: "Gestion des caisses",
    icon: "fa-box",
    color: "#EF6C00",
    action: "sm_boxes.sm_boxes_operations_action",
});