/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { patch } from "@web/core/utils/patch";

const userMenuRegistry = registry.category("user_menuitems");

// 1. Remove "Mon compte Odoo.com" (odoo_account)
if (userMenuRegistry.contains("odoo_account")) {
    userMenuRegistry.remove("odoo_account");
}

// 2. Remove standard "Aide" (support)
if (userMenuRegistry.contains("support")) {
    userMenuRegistry.remove("support");
}

// 3. Define the replacement Mizan item
export function mizanServiceItem(env) {
    return {
        type: "item",
        id: "mizan_service",
        description: _t("Service Mizan"),
        callback: () => {
            env.services.action.doAction({
                type: "ir.actions.client",
                tag: "sm_base.about_mizan",
                name: _t("Service Mizan"),
                target: "current",
            });
        },
        sequence: 10,
    };
}

// Add Mizan service item to the registry with sequence 10 (first item)
userMenuRegistry.add("mizan_service", mizanServiceItem, { sequence: 10 });

// Extra security: patch UserMenu to make sure odoo_account and support are never displayed
patch(UserMenu.prototype, {
    getElements() {
        const elements = super.getElements();
        return elements.filter((el) => el.id !== "odoo_account" && el.id !== "support");
    },
});
