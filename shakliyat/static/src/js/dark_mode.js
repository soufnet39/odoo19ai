/**
 * Shakliyat — dark mode toggle.
 *
 * Strategy:
 *   1. Read dark_mode from session (injected by session_info via ir_http.py).
 *   2. Add/remove data-theme="dark" on <body> → CSS rules apply dark colors.
 *   3. Debug logging to console for troubleshooting.
 *
 * CSS in shakliyat_dark.css only activates when [data-theme="dark"] is present.
 */
import { session } from "@web/session";

/**
 * Apply or remove dark mode based on the enabled flag.
 * @param {boolean} enabled - Whether dark mode should be active.
 */
function applyDarkMode(enabled) {
    if (enabled) {
        document.body.setAttribute("data-theme", "dark");
        console.log("[shakliyat] Dark mode ENABLED");
    } else {
        document.body.removeAttribute("data-theme");
        console.log("[shakliyat] Dark mode DISABLED");
    }
}

/**
 * Main entry: read dark_mode from session and apply.
 */
function initDarkMode() {
    const darkMode = session.dark_mode;
    console.log("[shakliyat] dark_mode from session:", darkMode, typeof darkMode);

    // Handle both boolean and string "true"/"false" from ir.config_parameter
    const isEnabled = darkMode === true || darkMode === "true";
    applyDarkMode(isEnabled);
}

// Start when the DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initDarkMode);
} else {
    initDarkMode();
}


