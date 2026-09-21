/**
 * Shakliyat — conditionally hide the Discuss application and its menus.
 *
 * Strategy:
 *   1. Read "hide_discuss" from session info (synchronous, no RPC).
 *   2. Fallback: read via RPC if session info is not yet available.
 *   3. Add .o_shakliyat_hide_discuss to <body> → CSS rules hide elements.
 *   4. MutationObserver catches elements added after initial render.
 */
import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";

/**
 * Hide Discuss-related elements in the DOM.
 * Targets by data-menu-xmlid (most reliable) and visible text (fallback).
 */
function hideDiscussElements() {
    document.querySelectorAll("*").forEach((el) => {
        if (shouldHide(el)) {
            const container = el.closest(
                "li, .o_app, .o_nav_entry, .o-dropdown-item, .o_systray_menu > *, .o_menu_systray > *"
            ) || el;
            container.style.display = "none";
        }
    });
}

/**
 * Determine if an element should be hidden (Discuss-related).
 */
function shouldHide(el) {
    // 1. data-menu-xmlid containing "mail." — most reliable
    const xmlid = el.getAttribute("data-menu-xmlid") || "";
    if (xmlid.includes("mail.") || xmlid.includes("discuss.")) {
        return true;
    }
    // 2. Visible text is exactly "discuss"
    const text = (el.textContent || "").trim().toLowerCase();
    if (text === "discuss") {
        return true;
    }
    // 3. Tooltip / title matches
    const title = (
        el.getAttribute("data-tooltip") || el.getAttribute("title") || ""
    ).toLowerCase();
    if (title === "discuss" || title === "chat") {
        return true;
    }
    return false;
}

/**
 * MutationObserver: watch for new elements and hide Discuss ones.
 */
function observeNewElements() {
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            for (const node of mutation.addedNodes) {
                if (node.nodeType !== Node.ELEMENT_NODE) continue;
                if (shouldHide(node)) {
                    const c = node.closest(
                        "li, .o_app, .o_nav_entry, .o-dropdown-item, .o_systray_menu > *, .o_menu_systray > *"
                    ) || node;
                    c.style.display = "none";
                }
                if (node.querySelectorAll) {
                    node.querySelectorAll("*").forEach((child) => {
                        if (shouldHide(child)) {
                            const c = child.closest(
                                "li, .o_app, .o_nav_entry, .o-dropdown-item, .o_systray_menu > *, .o_menu_systray > *"
                            ) || child;
                            c.style.display = "none";
                        }
                    });
                }
            }
        }
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

/**
 * Main entry: check if hiding is enabled and apply.
 */
async function applyHideDiscuss() {
    let hide = session.hide_discuss;

    // Fallback: if session info doesn't have the flag, fetch via RPC
    if (hide === undefined || hide === null) {
        try {
            hide = await rpc("/web/dataset/call_kw", {
                model: "ir.config.parameter",
                method: "get_param",
                args: ["shakliyat.hide_discuss"],
                kwargs: {},
            });
        } catch (e) {
            // RPC failed — cannot determine, skip
            return;
        }
    }

    // Normalize: handle string "True"/"False" and boolean
    const enabled =
        hide === true || hide === "True" || hide === "true" || hide === "1";
    if (!enabled) {
        return;
    }

    // 1. CSS class — hides elements via CSS rules (continuous)
    document.body.classList.add("o_shakliyat_hide_discuss");

    // 2. Immediate DOM scan — hide elements already in DOM
    hideDiscussElements();

    // 3. MutationObserver — catch dynamically-added elements (SPA nav, etc.)
    observeNewElements();
}

// Run as early as possible
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyHideDiscuss);
} else {
    applyHideDiscuss();
}
