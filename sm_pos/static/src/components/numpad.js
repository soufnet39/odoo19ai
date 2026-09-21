/** @odoo-module **/
import { Component } from "@odoo/owl";

export class Numpad extends Component {
    static template = "sm_pos.Numpad";
    static props = {
        onInput: Function,
        onBackspace: Function,
        onClear: Function,
    };

    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "0", "backspace"];
}