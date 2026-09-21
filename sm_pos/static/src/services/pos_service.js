/** @odoo-module **/
import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

export const posService = {
    dependencies: ["orm"],
    start(env, { orm }) {
        const service = reactive({
            session: null,
            config: null,
            products: [],
            categories: [],
            partners: [],
            paymentModes: [],
            order: null,

            newOrder() {
                this.order = {
                    id: false,
                    partner_id: false,
                    lines: [],
                    payments: [],
                };
            },

            async loadData() {
                const data = await orm.call("sm_pos.session", "load_pos_data", [this.session.id]);
                this.config = data.config;
                this.products = data.products;
                this.categories = data.categories;
                this.partners = data.partners;
                this.paymentModes = data.payment_modes;
                this.newOrder();
                return data;
            },

            async openSession(configId, openingCash) {
                const session = await orm.call("sm_pos.session", "open_session", [
                    configId,
                    openingCash,
                ]);
                this.session = session;
                await this.loadData();
                return session;
            },

            async closeSession(closingCash, notes) {
                const res = await orm.call("sm_pos.session", "close_session", [
                    this.session.id,
                    closingCash,
                    notes,
                ]);
                this.session = null;
                return res;
            },

            async startClosingControl() {
                const data = await orm.call("sm_pos.session", "start_closing_control", [
                    this.session.id,
                ]);
                this.session = data;
                return data;
            },

            async resumeSession() {
                const data = await orm.call("sm_pos.session", "resume_session", [
                    this.session.id,
                ]);
                this.session = data;
                return data;
            },

            addProduct(product) {
                const line = this.order.lines.find((l) => l.product_id === product.id);
                if (line) {
                    line.qty += 1;
                } else {
                    this.order.lines.push({
                        product_id: product.id,
                        name: product.name,
                        qty: 1,
                        unit_price: product.price,
                    });
                }
            },

            setQty(line, qty) {
                line.qty = Number(qty);
                if (line.qty <= 0) {
                    this.removeLine(line);
                }
            },

            incQty(line) {
                line.qty = Number(line.qty) + 1;
            },

            decQty(line) {
                line.qty = Number(line.qty) - 1;
                if (line.qty <= 0) {
                    this.removeLine(line);
                }
            },

            setPrice(line, price) {
                line.unit_price = price;
            },

            removeLine(line) {
                this.order.lines = this.order.lines.filter((l) => l !== line);
            },

            setPartner(partner) {
                this.order.partner_id = partner ? partner.id : false;
            },

            getOrderTotal() {
                return this.order.lines.reduce((sum, l) => sum + l.qty * l.unit_price, 0);
            },

            getPaidTotal() {
                return this.order.payments.reduce((sum, p) => sum + p.amount, 0);
            },

            async syncOrder() {
                const res = await orm.call("sm_pos.session", "sync_pos_order", [
                    this.session.id,
                    this.order,
                ]);
                this.order.id = res.id;
                return res;
            },

            async addPayment(paymentMode, amount) {
                const res = await orm.call("sm_pos.session", "add_payment", [
                    this.session.id,
                    this.order.id,
                    paymentMode.id,
                    amount,
                ]);
                this.order.payments.push({
                    payment_mode_id: paymentMode.id,
                    amount: amount,
                });
                return res;
            },
        });

        return service;
    },
};

registry.category("services").add("pos", posService);