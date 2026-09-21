/**
 * Shakliyat — form save/cancel buttons.
 *
 * Replaces the compact icon-only Save/Cancel buttons (web.FormStatusIndicator)
 * with normal, translatable text buttons: "Save" and "Cancel".
 *
 * The template strings are translated by Owl through Odoo's translation
 * function at render time, so the labels follow the user's language.
 */
import { FormStatusIndicator } from "@web/views/form/form_status_indicator/form_status_indicator";

// Point the core component at our template (applies before any form renders).
FormStatusIndicator.template = "shakliyat.FormStatusIndicator";
