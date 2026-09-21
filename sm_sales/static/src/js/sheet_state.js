/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("services").add("sm_sales_sheet_state", {
    dependencies: [],

    start() {
        setInterval(() => {
            const form = document.querySelector(".o_form_view");
            if (!form) return;

            const sheet = form.querySelector(".o_form_sheet");
            if (!sheet) return;

            sheet.classList.remove("sheet-state-draft", "sheet-state-confirmed", "sheet-state-canceled");

            const bar = form.querySelector(".o_statusbar_status");
            if (!bar) return;

            const activeBtn = bar.querySelector("button.o_arrow_button_current");
            if (!activeBtn) return;

            const text = activeBtn.textContent.trim().toLowerCase();
            const map = {
                "brouillon": "draft",
                "draft": "draft",
                "confirmée": "confirmed",
                "confirmed": "confirmed",
                "annulée": "canceled",
                "canceled": "canceled",
            };

            const cls = map[text];
            if (cls) {
                sheet.classList.add("sheet-state-" + cls);
            }
        }, 500);
    },
});
