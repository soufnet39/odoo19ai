/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class Numpad extends Component {
    static template = "sm_pos.Numpad";
    static props = {
        onKey: { type: Function, optional: true },
    };

    setup() {
        this.pos = useService("pos");
    }

    get activeMode() {
        return this.pos.numpadMode;
    }

    setMode(mode) {
        this.pos.setNumpadMode(mode);
    }

    press(key) {
        this.pos.handleNumpad(key);
        if (this.props.onKey) {
            this.props.onKey(key);
        }
    }
}