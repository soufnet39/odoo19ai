import { Dialog } from "@web/core/dialog/dialog";
import { _t } from "@web/core/l10n/translation";
import { useChildRef } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

/**
 * Shakliyat — three-way "unsaved changes" confirmation dialog.
 *
 * Shown when the user tries to leave a dirty form (routing change): the two
 * actions the core used to perform silently ("save", "discard") are now
 * offered to the user, plus a third "cancel" to abort the navigation and keep
 * editing.
 *
 * All visible strings go through _t, so they follow the user's language
 * (the same as the rest of the web client).
 */
export class LeaveConfirmDialog extends Component {
    static template = "shakliyat.LeaveConfirmDialog";
    static components = { Dialog };
    static props = {
        title: { type: String, optional: true },
        body: { type: String, optional: true },
        saveLabel: { type: String, optional: true },
        discardLabel: { type: String, optional: true },
        cancelLabel: { type: String, optional: true },
        onSave: { type: Function, optional: true },
        onDiscard: { type: Function, optional: true },
        onCancel: { type: Function, optional: true },
        close: { type: Function, optional: true },
    };
    static defaultProps = {
        title: _t("Unsaved changes"),
        body: _t("Would you like to save changes or discard them before leaving?"),
        saveLabel: _t("Save"),
        discardLabel: _t("Discard"),
        cancelLabel: _t("Cancel"),
    };

    setup() {
        this.modalRef = useChildRef();
    }

    onPressSave() {
        this.props.onSave?.();
        this.props.close?.();
    }

    onPressDiscard() {
        this.props.onDiscard?.();
        this.props.close?.();
    }

    onPressCancel() {
        this.props.onCancel?.();
        this.props.close?.();
    }
}
