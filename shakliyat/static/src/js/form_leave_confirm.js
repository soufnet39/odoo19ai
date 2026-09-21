import { FormController } from "@web/views/form/form_controller";
import { LeaveConfirmDialog } from "./leave_confirm_dialog";

/**
 * Shakliyat — confirm before leaving a dirty form.
 *
 * Core FormController.beforeLeave() silently auto-saves when a form is dirty
 * and the user navigates away (e.g. opens another menu / steps back), so the
 * user never gets to choose whether to save, discard or stay. Shakliyat
 * replaces that with an explicit Save / Discard / Cancel dialog.
 *
 * beforeLeave is called by the action service's clearUncommittedChanges()
 * during routing. Returning false aborts the navigation (Cancel); any other
 * choice preserves the original behaviour through the original beforeLeave.
 */
const _beforeLeave = FormController.prototype.beforeLeave;

FormController.prototype.beforeLeave = async function beforeLeave(options = {}) {
    const { forceLeave = false } = options;
    const root = this.model && this.model.root;
    const dirty = !!root && typeof root.isDirty === "function" && await root.isDirty();

    if (!forceLeave && dirty) {
        const choice = await this._shakliyat_confirmDirtyLeave();
        if (choice === "cancel") {
            // Keep the user on the form: abort navigation.
            return false;
        }
        if (choice === "discard") {
            // Drop the changes and let navigation proceed.
            await this.discard();
            return;
        }
        // "save" -> fall through to the original (silent auto-save) behaviour.
    }
    return _beforeLeave.call(this, options);
};

/**
 * Opens the three-way confirmation dialog and resolves with the chosen
 * action: "save" | "discard" | "cancel".
 *
 * dialogService.add accepts a 3rd `options` argument exposing onClose, which
 * fires on any dismissal (button click, ESC, backdrop, close icon), so the
 * promise always resolves — a dismissal without a labelled button is
 * treated as "cancel".
 */
FormController.prototype._shakliyat_confirmDirtyLeave = function _shakliyat_confirmDirtyLeave() {
    let choice = "cancel";
    return new Promise((resolve) => {
        this.dialogService.add(
            LeaveConfirmDialog,
            {
                onSave: () => {
                    choice = "save";
                },
                onDiscard: () => {
                    choice = "discard";
                },
                onCancel: () => {
                    choice = "cancel";
                },
            },
            {
                onClose: () => resolve(choice),
            }
        );
    });
};
