/**
 * Shakliyat — silver "Actions" button (cog menu replacement).
 *
 * The core CogMenu button is an icon-only gear (<i class="fa fa-fw fa-cog"/>).
 * Shakliyat replaces it with a solid silver button labelled "Actions" by
 * overriding the template of every CogMenu component:
 *
 *   - CogMenu        (graph / pivot / ... views)        -> shakliyat.CogMenu
 *   - FormCogMenu    (form views)                      -> shakliyat.FormCogMenu
 *   - ListCogMenu    (list views)                      -> shakliyat.ListCogMenu
 *   - KanbanCogMenu  (kanban views)                    -> shakliyat.KanbanCogMenu
 *
 * Each shakliyat template inherits from the corresponding web.* template and
 * applies the same xpath patches (icon → text, button class change), plus the
 * view-specific patches (t-if condition, separators) that the original
 * sub-templates define. This avoids the blockId ordering issue that
 * t-inherit-mode="extension" suffers from in Odoo 19's asset loader, where
 * extensions registered after a template block are not retroactively applied
 * to templates that already inherited from the extended parent.
 *
 * Additionally, the entire web.FormView template is overridden (shakliyat.FormView)
 * to move the <CogMenu> from the control-panel-additional-actions slot to the
 * control-panel-status-indicator slot, so the "Actions" button renders as a
 * sibling of the Save / Cancel buttons in the form status indicator.
 *
 * The "Actions" label is a plain string in the XML template, so it goes
 * through Odoo's translation pipeline at render time (same mechanism as the
 * existing data-tooltip="Actions" attribute).
 */
import { FormController } from "@web/views/form/form_controller";
import { CogMenu } from "@web/search/cog_menu/cog_menu";
import { FormCogMenu } from "@web/views/form/form_cog_menu/form_cog_menu";
import { ListCogMenu } from "@web/views/list/list_cog_menu";
import { KanbanCogMenu } from "@web/views/kanban/kanban_cog_menu";

// Override the CogMenu component templates (icon → "Actions" text, silver btn).
CogMenu.template = "shakliyat.CogMenu";
FormCogMenu.template = "shakliyat.FormCogMenu";
ListCogMenu.template = "shakliyat.ListCogMenu";
KanbanCogMenu.template = "shakliyat.KanbanCogMenu";

// Override the FormView template so the CogMenu (Actions button) is moved
// from the control-panel-additional-actions slot to the status-indicator slot,
// placing it as a sibling of the Save / Cancel buttons.
FormController.template = "shakliyat.FormView";
