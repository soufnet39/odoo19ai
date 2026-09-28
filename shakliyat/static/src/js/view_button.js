import { patch } from "@web/core/utils/patch";
import { ViewButton } from "@web/views/view_button/view_button";
import { evaluateBooleanExpr } from "@web/core/py_js/py";

/**
 * Shakliyat — enable dynamic `disabled="..."` expressions on view buttons.
 *
 * In standard Odoo, `<button disabled="..."/>` is only treated as a static
 * string literal. This patch evaluates Python-like boolean expressions inside
 * `disabled="..."` against the record context (identically to `invisible="..."`),
 * dynamically disabling the button (HTML disabled attribute + Bootstrap styling)
 * while keeping it visible on screen.
 */
patch(ViewButton.prototype, {
    get disabled() {
        const { name, type, special } = this.clickParams;
        if (!name && !type && !special) {
            return true;
        }
        if (!this.props.disabled) {
            return false;
        }
        if (
            this.props.disabled === "disabled" ||
            this.props.disabled === "1" ||
            this.props.disabled === "True" ||
            this.props.disabled === true
        ) {
            return true;
        }
        if (
            this.props.disabled === "0" ||
            this.props.disabled === "False" ||
            this.props.disabled === false
        ) {
            return false;
        }
        if (this.props.record) {
            try {
                const evalContext =
                    this.props.record.evalContextWithVirtualIds ||
                    this.props.record.evalContext ||
                    {};
                return Boolean(evaluateBooleanExpr(this.props.disabled, evalContext));
            } catch {
                return false;
            }
        }
        return false;
    },

    onClick(ev, newWindow) {
        if (this.disabled) {
            ev.preventDefault();
            ev.stopPropagation();
            return;
        }
        return super.onClick(...arguments);
    },
});
